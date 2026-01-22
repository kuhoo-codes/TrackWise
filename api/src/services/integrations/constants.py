# Patterns to strictly ignore
IGNORED_PATTERNS = [
    "*.lock",
    "package-lock.json",
    "dist/*",
    "build/*",
    "node_modules/*",
    "*.min.js",
    ".DS_Store",
    "*.map",
]

WEIGHTS = {
    "HIGH": 1.0,  # Core Logic
    "MEDIUM": 0.5,  # Infra/Config
    "LOW": 0.1,  # Documentation/Minor Config
}


HIGH_VALUE_EXTS = {".py", ".ts", ".tsx", ".rs", ".go", ".java", ".cpp", ".c", ".h", ".swift", ".kt", ".rb"}
MEDIUM_VALUE_FILES = {"Dockerfile", "docker-compose.yml", "schema.prisma"}
LOW_VALUE_EXTS = {".md", ".txt", ".gitignore", ".env.example", ".json"}

THRESHOLD_FEATURE = 20.0
THRESHOLD_REFACTOR = 5.0

# Cap per file to prevent skewed data from massive generated files
MAX_LINES_PER_FILE_CAP = 500
