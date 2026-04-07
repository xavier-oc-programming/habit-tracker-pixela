import re

# API / URLs
PIXELA_BASE = "https://pixe.la/v1/users"

# Graph defaults
GRAPH_ID = "graph1"
GRAPH_NAME = "Running Graph"
GRAPH_UNIT = "Km"
GRAPH_TYPE = "float"   # "int" or "float"
GRAPH_COLOR = "sora"   # see VALID_COLORS
VALID_COLORS = ["shibafu", "momiji", "sora", "ichou", "ajisai", "kuro"]

# Validation
USERNAME_RULE = re.compile(r"^[a-z][a-z0-9-]{1,32}$")
GRAPH_ID_RULE = re.compile(r"^[a-zA-Z][a-zA-Z0-9]{0,15}$")
MIN_TOKEN_LEN = 8

# Output / formatting
DATE_FORMAT = "%Y%m%d"
DATE_DISPLAY = "%Y-%m-%d"
