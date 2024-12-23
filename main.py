import re
import sys
import xml.etree.ElementTree as ET


class Tokenizer:
    """Лексический анализатор для учебного конфигурационного языка."""

    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        """Разделяет текст на токены."""
        patterns = [
            (r"#\((.*?)\)", "ARRAY"),  # Массив
            (r"%\{.*?%\}", "MULTILINE_COMMENT"),  # Многострочный комментарий
            (r"\*.*", "SINGLELINE_COMMENT"),  # Однострочный комментарий
            (r"global\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.*?);", "GLOBAL"),  # Константа
            (r"\?\[([a-zA-Z][_a-zA-Z0-9]*)\]", "CONSTANT_EVAL"),  # Вычисление константы
            (r"\{", "DICT_START"),  # Начало словаря
            (r"\}", "DICT_END"),  # Конец словаря
            (r"([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.*)", "KEY_VALUE"),  # Пары ключ-значение
            (r"[0-9]+", "NUMBER"),  # Числа
        ]

        for pattern, token_type in patterns:
            matches = re.finditer(pattern, self.text, re.DOTALL)
            for match in matches:
                self.tokens.append((token_type, match.group(0)))

    def get_tokens(self):
        """Возвращает список токенов."""
        return self.tokens


class Parser:
    """Синтаксический анализатор для учебного конфигурационного языка."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.constants = {}

    def parse(self):
        """Парсит токены и возвращает дерево разбора."""
        root = ET.Element("config")
        while self.index < len(self.tokens):
            token_type, token_value = self.tokens[self.index]
            if token_type == "GLOBAL":
                self.parse_global(token_value, root)
            elif token_type == "DICT_START":
                self.parse_dict(root)
            elif token_type == "ARRAY":
                self.parse_array(token_value, root)
            elif token_type == "CONSTANT_EVAL":
                self.parse_constant_eval(token_value, root)
            self.index += 1
        return root

    def parse_global(self, token_value, root):
        """Парсит глобальную константу."""
        match = re.match(r"global\s+([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.*?);", token_value)
        if match:
            name, value = match.groups()
            self.constants[name] = value
            const_elem = ET.SubElement(root, "global")
            const_elem.set("name", name)
            const_elem.text = value

    def parse_dict(self, root):
        """Парсит словарь."""
        dict_elem = ET.SubElement(root, "dict")
        self.index += 1
        while self.tokens[self.index][0] != "DICT_END":
            token_type, token_value = self.tokens[self.index]
            if token_type == "KEY_VALUE":
                key, value = token_value.split("=")
                key = key.strip()
                value = value.strip()
                item_elem = ET.SubElement(dict_elem, "item")
                item_elem.set("key", key)
                item_elem.text = value
            self.index += 1

    def parse_array(self, token_value, root):
        """Парсит массив."""
        match = re.match(r"#\((.*?)\)", token_value)
        if match:
            values = match.group(1).split(",")
            array_elem = ET.SubElement(root, "array")
            for value in values:
                value_elem = ET.SubElement(array_elem, "value")
                value_elem.text = value.strip()

    def parse_constant_eval(self, token_value, root):
        """Парсит вычисление константы."""
        match = re.match(r"\?\[([a-zA-Z][_a-zA-Z0-9]*)\]", token_value)
        if match:
            name = match.group(1)
            value = self.constants.get(name, "undefined")
            const_eval_elem = ET.SubElement(root, "constant_eval")
            const_eval_elem.set("name", name)
            const_eval_elem.text = value


class Translator:
    """Инструмент для перевода конфигурационного языка в XML."""

    def __init__(self, text):
        self.text = text

    def translate(self):
        """Переводит текст в XML."""
        tokenizer = Tokenizer(self.text)
        tokens = tokenizer.get_tokens()
        parser = Parser(tokens)
        tree = parser.parse()
        return ET.tostring(tree, encoding="unicode")


if __name__ == "__main__":
    input_text = sys.stdin.read()
    translator = Translator(input_text)
    try:
        xml_output = translator.translate()
        print(xml_output)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)