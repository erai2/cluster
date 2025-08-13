import sqlite3
import re
from datetime import datetime

class SuamSaJuAnalyzer:
    def __init__(self, db_path="suri_myeongri.db"):
        # \ub370\uc774\ud130\ubca0\uc774\uc2a4 \uc5f0\uacb0 \ubc0f \ud14c\uc774\ube14 \uc0dd\uc131
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # \uae30\ubcf8 \uc774\ub860 \ud14c\uc774\ube14
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS basic_theory (
            id INTEGER PRIMARY KEY,
            category TEXT,
            concept TEXT,
            description TEXT
        )
        ''')

        # \uc6a9\uc5b4 \uc0ac\uc804 \ud14c\uc774\ube14
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS terminology (
            id INTEGER PRIMARY KEY,
            term TEXT,
            meaning TEXT,
            category TEXT
        )
        ''')

        # \uc0ac\uc8fc \ubd84\uc11d \uc0ac\ub840 \ud14c\uc774\ube14
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_studies (
            id INTEGER PRIMARY KEY,
            birth_date TEXT,
            birth_time TEXT,
            gender TEXT,
            saju TEXT,
            analysis TEXT,
            result TEXT
        )
        ''')

        self.conn.commit()

    def add_basic_theory(self, category, concept, description):
        self.cursor.execute(
            "INSERT INTO basic_theory (category, concept, description) VALUES (?, ?, ?)",
            (category, concept, description)
        )
        self.conn.commit()

    def add_terminology(self, term, meaning, category):
        self.cursor.execute(
            "INSERT INTO terminology (term, meaning, category) VALUES (?, ?, ?)",
            (term, meaning, category)
        )
        self.conn.commit()

    def search_concept(self, keyword):
        self.cursor.execute(
            "SELECT * FROM basic_theory WHERE category LIKE ? OR concept LIKE ? OR description LIKE ?",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        return self.cursor.fetchall()

    def analyze_saju(self, saju_text):
        # \uc0ac\uc8fc \ubd84\uc11d \ub85c\uc9c1 \uad6c\ud604
        # 1. \uc8fc\uc704\uc640 \ube48\uc704 \uad6c\ubd84
        # 2. \uccb4\uc640 \uc6a9 \ubd84\uc11d
        # 3. \uc81c\uc555 \ubc29\uc2dd \ud655\uc778
        # 4. \uc6a9\uc2e0\uacfc \uae30\uc2e0 \ud310\ubc95
        # 5. \uc5f0\ub7b5\uacfc \ud6a8\uc728 \uacc4\uc0b0

        # \uc608\uc2dc \ucf54\ub4dc (\uc2e4\uc81c \uad6c\ud604\uc740 \ub354 \ubcf5\uc7a1\ud569\ub2c8\ub2e4)
        analysis = {}

        # \uc8fc\uc704/\ube48\uc704 \uad6c\ubd84
        day_stem = saju_text[4:5]  # \uc77c\uac04 \ucd94\ucd9c (\uac74\ub108\ud558 \uc608\uc2dc)
        analysis['main_position'] = f"\uc77c\uac04: {day_stem}, \uc77c\uc8fc \ubc0f \uc2dc\uc8fc"
        analysis['guest_position'] = "\ub144\uc8fc, \uc6d4\uc8fc, \ub300\uc6b4, \uc138\uc6b4"

        # \uccb4\uc640 \uc6a9 \ubd84\uc11d
        analysis['che'] = "\ube44\uac04, \uac81\uc7ac, \uc778\uc131, \ub85c\ud06c, \uc591\uc778 (\ub0b4 \ud798, \uc138\ub825)"
        analysis['yong'] = "\uc7ac\uc131, \uad00\uc131 (\uc5bb\uace0\uc790 \ud558\ub294 \ubaa9\ud45c)"

        return analysis

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    analyzer = SuamSaJuAnalyzer()

    # \uae30\ubcf8 \uc774\ub860 \ub370\uc774\ud130 \ucd94\uac00
    analyzer.add_basic_theory("\uae30\ubcf8\uc6d0\ub9ac", "\uc8fc\uc704\uc640 \ube48\uc704", "\uc8fc\uc704(\uc601\uc9c0): \ubd88\uc778\uc774 \uad00\ub9ac \ud1b5\uc81c\uac00 \uac00\ub2a5\ud55c \uc9c0\uc5ed, \ube48\uc704(\ud0c0\uc9c0): \ubd88\uc778\uc774 \uad00\ub9ac \ud1b5\uc81c\uac00 \ubd88\uac00\ub2a5\ud55c \uc9c0\uc5ed")
    analyzer.add_basic_theory("\uae30\ubcf8\uc6d0\ub9ac", "\uccb4\uc640 \uc6a9", "\uccb4: \ub098\uac00 \uac00\uc9c0\uace0 \uc788\ub294 \ud798, \uc0ac\uc6a9\ud558\ub294 \ub3c4\uad6c, \uc6a9: \ub098\uac00 \ucd94\uad6c\ud558\ub294 \ubaa9\ud45c(\uc7ac\ubb3c, \uad8c\ub825 \ub4f1)")
    analyzer.add_basic_theory("\uc81c\uc555\ubc29\uc2dd", "\uc21c\ud589\uc81c\uc555", "\uc8fc\uc704\uc758 \uccb4\uac00 \ube48\uc704\uc758 \uc6a9\uc744 \uce58\ud558\ub294 \uc81c\uc555\ubc29\uc2dd")
    analyzer.add_basic_theory("\uc81c\uc555\ubc29\uc2dd", "\uc5ed\ud589\uc81c\uc555", "\ube48\uc704\uc758 \uccb4\uac00 \uc8fc\uc704\uc758 \uc6a9\uc744 \uce58\ud558\ub294 \uc81c\uc555\ubc29\uc2dd")

    # \uc6a9\uc5b4 \ucd94\uac00
    analyzer.add_terminology("\uc801\uc2e0", "\uc81c\uc555\uc744 \ub2f4\ud558\ub294 \ucf1c", "\uc81c\uc555\uad6c\uc870")
    analyzer.add_terminology("\ud3ec\uc2e0", "\uc81c\uc555\uc744 \ud558\ub294 \ucf1c", "\uc81c\uc555\uad6c\uc870")

    # \uc0ac\uc8fc \ubd84\uc11d \uc608\uc2dc
    sample_saju = "\uac11\uc778 \ubcd1\uc624 \uc815\ubbf8 \ubb34\uc2e0"
    result = analyzer.analyze_saju(sample_saju)
    print(result)

    # \uac80\uc0c9 \uc608\uc2dc
    search_results = analyzer.search_concept("\uccb4\uc640 \uc6a9")
    print(search_results)

    analyzer.close()
