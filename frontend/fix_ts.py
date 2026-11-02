import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix React unused import
    content = re.sub(r"import React(?:, \{[^}]+\})? from 'react';\n", lambda m: m.group(0).replace("import React, ", "import ").replace("import React from 'react';\n", ""), content)

    # In case the regex above missed something:
    content = content.replace("import React from 'react';\n", "")
    content = content.replace("import React, ", "import ")

    # Fix lucide-react imports in ProfileCard
    if "ProfileCard.tsx" in filepath:
        content = content.replace("Linkedin, Github, ", "")
        content = content.replace(", Award", "")
        content = content.replace("<Linkedin className=\"w-4 h-4 mr-1\" />", "")
        content = content.replace("<Github className=\"w-4 h-4 mr-1\" />", "")

    # Fix checkCircle, FileText, Target, BarChart3, Tag in various files
    content = re.sub(r", CheckCircle", "", content)
    content = re.sub(r", FileText", "", content)
    content = re.sub(r", Target", "", content)
    content = re.sub(r"BarChart3, ", "", content)
    content = re.sub(r", Tag", "", content)

    # Fix AuthContext.tsx ReactNode import
    if "AuthContext.tsx" in filepath:
        content = content.replace("import { createContext, useContext, useState, useEffect, ReactNode } from 'react';", "import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';")

    # Fix ../utils/api and ../api/apiClient to ../services/api
    content = content.replace("from '../utils/api'", "from '../services/api'")
    content = content.replace("from '../api/apiClient'", "from '../services/api'")

    # Fix AnalysisDashboard.tsx python types (str, int)
    content = re.sub(r": str\b", ": string", content)
    content = re.sub(r": int\b", ": number", content)

    # Fix strictNullChecks stats.easy
    if "CompanyDetails.tsx" in filepath:
        content = content.replace("stats.easy", "stats?.easy")
        content = content.replace("stats.medium", "stats?.medium")
        content = content.replace("stats.hard", "stats?.hard")

    # Fix motion unused
    if "Dashboard.tsx" in filepath:
        content = content.replace("import { motion } from 'framer-motion';\n", "")

    # Fix useAuth unused in ResumeHistory
    if "ResumeHistory.tsx" in filepath:
        content = content.replace("import { useAuth } from '../context/AuthContext';\n", "")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

src_dir = "src"
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith((".tsx", ".ts")):
            fix_file(os.path.join(root, file))
