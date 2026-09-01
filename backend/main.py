import os
import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, List, Optional, Tuple
import re
import base64
import traceback
import urllib.request
from pydantic import ValidationError

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import find_dotenv, load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.agents.banca_agent import get_banca_agent
from app.agents.edital_agent import get_edital_agent
from app.agents.prova_agent import get_prova_agent
from app.agents.questoes_agent import completar_questao, gerar_questoes, gerar_questoes_com_imagens
from app.models.schemas import AnaliseBanca, AnaliseProva, Edital, ListaQuestoes
from app.services.file_service import extrair_texto_arquivo

load_dotenv(find_dotenv())


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalyzeBancaRequest(BaseModel):
    nome_banca: str


class AnalyzeTextRequest(BaseModel):
    texto: str


class ProvaFigurasResponse(BaseModel):
    ratio: float
    total_questoes: int
    total_figuras: int
    figuras: List[str]


class GenerateQuestionsRequest(BaseModel):
    materia: str
    assunto: str
    quantidade: int
    dificuldade: str
    nivel_ensino: Optional[str] = None
    num_alternativas: int = 5
    incluir_texto_base: bool = False
    modo_texto_base: Optional[str] = None
    texto_base_fornecido: Optional[str] = None
    analise_banca: Optional[AnaliseBanca] = None
    analise_prova: Optional[AnaliseProva] = None
    edital: Optional[Edital] = None


class CompleteQuestionRequest(BaseModel):
    enunciado: str
    materia: str
    assunto: str
    num_alternativas: int = 5
    analise_banca: Optional[AnaliseBanca] = None
    analise_prova: Optional[AnaliseProva] = None


class CreateUserRequest(BaseModel):
    email: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    email: str
    is_admin: bool


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    if val is None or not str(val).strip():
        return default
    return val


JWT_SECRET = _env("JWT_SECRET", "change-me")
JWT_ALG = _env("JWT_ALG", "HS256")
JWT_EXPIRES_MIN = int(_env("JWT_EXPIRES_MIN", "120") or "120")

ADMIN_EMAIL = _env("ADMIN_EMAIL")
ADMIN_PASSWORD = _env("ADMIN_PASSWORD")

USERS_FILE_PATH = Path(
    _env("USERS_FILE_PATH", os.path.join(os.path.dirname(__file__), "users.json"))
    or os.path.join(os.path.dirname(__file__), "users.json")
)
_users_lock = threading.Lock()


def _split_origins(value: Optional[str]) -> List[str]:
    if not value or not str(value).strip():
        return ["*"]
    if str(value).strip() == "*":
        return ["*"]
    origins = [o.strip() for o in value.split(",") if o.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


# #region debug-point A:report-helper
def _debug_report(hypothesis_id: str, location: str, msg: str, data: Optional[dict] = None, run_id: str = "pre-fix") -> None:
    payload = {
        "sessionId": "config-fetch-error",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "msg": msg,
        "data": data or {},
    }
    url = "http://127.0.0.1:7777/event"
    env_path = Path(".dbg/config-fetch-error.env")
    try:
        if env_path.exists():
            env_text = env_path.read_text(encoding="utf-8")
            for line in env_text.splitlines():
                if line.startswith("DEBUG_SERVER_URL="):
                    url = line.split("=", 1)[1].strip() or url
                    break
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1).read()
    except Exception:
        pass
# #endregion


def _raise_agent_http_error(raw: Any, context: str) -> None:
    text = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
    lower = text.lower()
    if "resource_exhausted" in lower or "quota exceeded" in lower or "\"code\": 429" in lower:
        retry_match = re.search(r"retry in ([0-9]+(?:[\\.,][0-9]+)?)s", text, flags=re.IGNORECASE)
        if not retry_match:
            retry_match = re.search(r"\"retryDelay\"\s*:\s*\"([0-9]+(?:[\\.,][0-9]+)?)s\"", text, flags=re.IGNORECASE)
        retry_hint = ""
        if retry_match:
            retry_seconds = retry_match.group(1).replace(",", ".")
            try:
                retry_pretty = str(max(1, round(float(retry_seconds))))
            except Exception:
                retry_pretty = retry_seconds
            retry_hint = f" Tente novamente em cerca de {retry_pretty}s."
        raise HTTPException(status_code=429, detail=f"Limite temporário da API Gemini atingido ao processar {context}.{retry_hint}")
    raise HTTPException(status_code=502, detail=f"A IA retornou uma resposta inválida ao processar {context}.")


def _coerce_agent_content(resp: Any, model_cls: Any, context: str) -> Any:
    content = getattr(resp, "content", None)
    if isinstance(content, model_cls):
        return content
    try:
        if isinstance(content, dict):
            return model_cls.model_validate(content)
        if isinstance(content, str):
            return model_cls.model_validate_json(content)
    except ValidationError:
        _raise_agent_http_error(content, context)
    except Exception:
        _raise_agent_http_error(content, context)
    _raise_agent_http_error(content, context)


app = FastAPI(title="ConcursoAI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_split_origins(_env("CORS_ORIGINS")),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# #region debug-point B:request-middleware
@app.middleware("http")
async def _debug_request_middleware(request, call_next):
    origin = request.headers.get("origin")
    auth_present = bool(request.headers.get("authorization"))
    path = request.url.path
    _debug_report("B", "backend/main.py:middleware:entry", "[DEBUG] request-start", {"path": path, "method": request.method, "origin": origin, "auth_present": auth_present})
    try:
        response = await call_next(request)
        _debug_report("B", "backend/main.py:middleware:exit", "[DEBUG] request-end", {"path": path, "status_code": response.status_code, "origin": origin})
        return response
    except Exception as exc:
        _debug_report("A", "backend/main.py:middleware:exception", "[DEBUG] request-exception", {"path": path, "origin": origin, "error_type": type(exc).__name__, "error": str(exc), "traceback": traceback.format_exc()[-4000:]})
        raise
# #endregion


def _load_users() -> dict:
    if not USERS_FILE_PATH.exists():
        return {}
    raw = USERS_FILE_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if isinstance(data, dict):
        return data
    return {}


def _save_users(users: dict) -> None:
    USERS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def _init_users() -> None:
    with _users_lock:
        users = _load_users()
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            email = ADMIN_EMAIL.strip().lower()
            users[email] = {"password_hash": pwd_context.hash(ADMIN_PASSWORD), "is_admin": True}
        _save_users(users)


@app.on_event("startup")
def _on_startup() -> None:
    _init_users()
    # #region debug-point D:startup-config
    _debug_report("D", "backend/main.py:startup", "[DEBUG] startup-config", {"cors_origins_env": _env("CORS_ORIGINS"), "loaded_origins": _split_origins(_env("CORS_ORIGINS")), "users_file": str(USERS_FILE_PATH), "dotenv_found": find_dotenv()})
    # #endregion


def _create_token(email: str, is_admin: bool) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "is_admin": bool(is_admin),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRES_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def _get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            # #region debug-point E:auth-empty-sub
            _debug_report("E", "backend/main.py:_get_current_user", "[DEBUG] auth-invalid-empty-sub", {})
            # #endregion
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": str(sub), "is_admin": bool(payload.get("is_admin"))}
    except JWTError:
        # #region debug-point E:auth-jwt-error
        _debug_report("E", "backend/main.py:_get_current_user", "[DEBUG] auth-jwt-error", {})
        # #endregion
        raise HTTPException(status_code=401, detail="Token inválido")


def _require_auth(user: dict = Depends(_get_current_user)) -> dict:
    return user


def _require_admin(user: dict = Depends(_get_current_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


class _UploadShim:
    def __init__(self, filename: str, content: bytes):
        self.name = filename
        self._content = content

    def read(self) -> bytes:
        return self._content


async def _read_text_or_file(texto: Optional[str], arquivo: Optional[UploadFile]) -> str:
    if texto and texto.strip():
        return texto.strip()
    if arquivo is None:
        raise HTTPException(status_code=400, detail="Informe texto ou envie arquivo")
    content = await arquivo.read()
    shim = _UploadShim(arquivo.filename or "arquivo", content)
    return extrair_texto_arquivo(shim)


def _estimar_total_questoes(texto: str) -> int:
    if not texto:
        return 0
    normalized = texto.replace("\r\n", "\n")
    matches = re.findall(r"(?:^|\n)\s*(?:Quest[aã]o\s*)?(\d{1,3})\s*[\)\.\-]\s+", normalized, flags=re.IGNORECASE)
    nums = []
    for m in matches:
        try:
            nums.append(int(m))
        except ValueError:
            continue
    if not nums:
        return 0
    return max(nums)


def _extract_figuras_pdf(pdf_bytes: bytes, max_figuras: int = 30) -> List[Tuple[bytes, str]]:
    try:
        import fitz  # type: ignore
    except Exception:
        raise HTTPException(status_code=400, detail="Dependência PyMuPDF ausente (pymupdf). Instale com: pip install pymupdf")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    figuras: List[Tuple[bytes, str]] = []
    try:
        for page in doc:
            if len(figuras) >= max_figuras:
                break
            images = page.get_images(full=True) or []
            for img in images:
                if len(figuras) >= max_figuras:
                    break
                xref = img[0]
                data = doc.extract_image(xref)
                img_bytes = data.get("image")
                ext = (data.get("ext") or "png").lower()
                if not isinstance(img_bytes, (bytes, bytearray)):
                    continue
                mime = "image/png"
                if ext in ("jpg", "jpeg"):
                    mime = "image/jpeg"
                elif ext == "webp":
                    mime = "image/webp"
                figuras.append((bytes(img_bytes), mime))
    finally:
        doc.close()

    return figuras


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    email = body.email.strip().lower()
    with _users_lock:
        users = _load_users()
        record = users.get(email)
    if not record:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not pwd_context.verify(body.password, record.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return LoginResponse(access_token=_create_token(email, bool(record.get("is_admin"))))


@app.get("/auth/me")
def me(user: dict = Depends(_require_auth)) -> dict:
    return {"email": user["email"], "is_admin": user.get("is_admin", False)}


@app.post("/auth/users", response_model=UserResponse)
def create_user(body: CreateUserRequest, _: dict = Depends(_require_admin)) -> UserResponse:
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email inválido")
    if not body.password or len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Senha muito curta")
    with _users_lock:
        users = _load_users()
        if email in users:
            raise HTTPException(status_code=409, detail="Usuário já existe")
        users[email] = {"password_hash": pwd_context.hash(body.password), "is_admin": bool(body.is_admin)}
        _save_users(users)
    return UserResponse(email=email, is_admin=bool(body.is_admin))


@app.post("/analyze/edital", response_model=Edital)
async def analyze_edital(
    texto: Optional[str] = Form(default=None),
    arquivo: Optional[UploadFile] = File(default=None),
    _: dict = Depends(_require_auth),
) -> Edital:
    # #region debug-point C:analyze-edital-entry
    _debug_report("C", "backend/main.py:analyze_edital:entry", "[DEBUG] analyze-edital-entry", {"texto_len": len((texto or "").strip()), "arquivo_nome": arquivo.filename if arquivo else None})
    # #endregion
    conteudo = await _read_text_or_file(texto, arquivo)
    # #region debug-point C:analyze-edital-content
    _debug_report("C", "backend/main.py:analyze_edital:content", "[DEBUG] analyze-edital-content", {"conteudo_len": len(conteudo)})
    # #endregion
    agent = get_edital_agent()
    resp = agent.run(conteudo)
    # #region debug-point C:analyze-edital-success
    _debug_report("C", "backend/main.py:analyze_edital:success", "[DEBUG] analyze-edital-success", {"has_content": bool(resp and getattr(resp, "content", None))})
    # #endregion
    return _coerce_agent_content(resp, Edital, "análise do edital")


@app.post("/analyze/banca", response_model=AnaliseBanca)
def analyze_banca(body: AnalyzeBancaRequest, _: dict = Depends(_require_auth)) -> AnaliseBanca:
    # #region debug-point C:analyze-banca-entry
    _debug_report("C", "backend/main.py:analyze_banca:entry", "[DEBUG] analyze-banca-entry", {"nome_banca": body.nome_banca})
    # #endregion
    agent = get_banca_agent()
    resp = agent.run(body.nome_banca)
    # #region debug-point C:analyze-banca-success
    _debug_report("C", "backend/main.py:analyze_banca:success", "[DEBUG] analyze-banca-success", {"has_content": bool(resp and getattr(resp, "content", None))})
    # #endregion
    return _coerce_agent_content(resp, AnaliseBanca, "análise da banca")


@app.post("/analyze/prova", response_model=AnaliseProva)
async def analyze_prova(
    texto: Optional[str] = Form(default=None),
    arquivo: Optional[UploadFile] = File(default=None),
    _: dict = Depends(_require_auth),
) -> AnaliseProva:
    # #region debug-point C:analyze-prova-entry
    _debug_report("C", "backend/main.py:analyze_prova:entry", "[DEBUG] analyze-prova-entry", {"texto_len": len((texto or "").strip()), "arquivo_nome": arquivo.filename if arquivo else None})
    # #endregion
    conteudo = await _read_text_or_file(texto, arquivo)
    # #region debug-point C:analyze-prova-content
    _debug_report("C", "backend/main.py:analyze_prova:content", "[DEBUG] analyze-prova-content", {"conteudo_len": len(conteudo)})
    # #endregion
    agent = get_prova_agent()
    resp = agent.run(conteudo)
    # #region debug-point C:analyze-prova-success
    _debug_report("C", "backend/main.py:analyze_prova:success", "[DEBUG] analyze-prova-success", {"has_content": bool(resp and getattr(resp, "content", None))})
    # #endregion
    return _coerce_agent_content(resp, AnaliseProva, "análise da prova")


@app.post("/analyze/prova-figures", response_model=ProvaFigurasResponse)
async def analyze_prova_figures(
    arquivo: UploadFile = File(...),
    _: dict = Depends(_require_auth),
) -> ProvaFigurasResponse:
    if not (arquivo.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")
    pdf_bytes = await arquivo.read()
    figuras = _extract_figuras_pdf(pdf_bytes, max_figuras=30)

    shim = _UploadShim(arquivo.filename or "prova.pdf", pdf_bytes)
    texto = extrair_texto_arquivo(shim)
    total_questoes = _estimar_total_questoes(texto)
    total_figuras = len(figuras)
    ratio = 0.0
    if total_questoes > 0:
        ratio = min(1.0, total_figuras / float(total_questoes))

    data_urls = []
    for img_bytes, mime in figuras:
        b64 = base64.b64encode(img_bytes).decode("ascii")
        data_urls.append(f"data:{mime};base64,{b64}")

    return ProvaFigurasResponse(
        ratio=ratio,
        total_questoes=total_questoes,
        total_figuras=total_figuras,
        figuras=data_urls,
    )


@app.post("/questions/generate", response_model=ListaQuestoes)
def generate_questions(body: GenerateQuestionsRequest, _: dict = Depends(_require_auth)) -> ListaQuestoes:
    return gerar_questoes(
        materia=body.materia,
        assunto=body.assunto,
        quantidade=body.quantidade,
        dificuldade=body.dificuldade,
        nivel_ensino=body.nivel_ensino,
        num_alternativas=body.num_alternativas,
        incluir_texto_base=body.incluir_texto_base,
        modo_texto_base=body.modo_texto_base,
        texto_base_fornecido=body.texto_base_fornecido,
        analise_banca=body.analise_banca,
        analise_prova=body.analise_prova,
        edital=body.edital,
    )


@app.post("/questions/generate-with-images", response_model=ListaQuestoes)
async def generate_questions_with_images(
    materia: str = Form(...),
    assunto: str = Form(...),
    dificuldade: str = Form(...),
    num_alternativas: int = Form(5),
    analise_banca_json: Optional[str] = Form(default=None),
    analise_prova_json: Optional[str] = Form(default=None),
    edital_json: Optional[str] = Form(default=None),
    images: List[UploadFile] = File(...),
    _: dict = Depends(_require_auth),
) -> ListaQuestoes:
    items = []
    for img in images:
        content = await img.read()
        mime = img.content_type or "image/png"
        items.append((content, mime))
    analise_banca = None
    analise_prova = None
    edital = None
    try:
        if analise_banca_json:
            analise_banca = AnaliseBanca.model_validate_json(analise_banca_json)
        if analise_prova_json:
            analise_prova = AnaliseProva.model_validate_json(analise_prova_json)
        if edital_json:
            edital = Edital.model_validate_json(edital_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos para contexto (banca/prova/edital).")
    return gerar_questoes_com_imagens(
        materia=materia,
        assunto=assunto,
        imagens=items,
        dificuldade=dificuldade,
        num_alternativas=num_alternativas,
        analise_banca=analise_banca,
        analise_prova=analise_prova,
        edital=edital,
    )


@app.post("/questions/complete", response_model=ListaQuestoes)
def complete_question(body: CompleteQuestionRequest, _: dict = Depends(_require_auth)) -> ListaQuestoes:
    return completar_questao(
        enunciado=body.enunciado,
        materia=body.materia,
        assunto=body.assunto,
        num_alternativas=body.num_alternativas,
        analise_banca=body.analise_banca,
        analise_prova=body.analise_prova,
    )
