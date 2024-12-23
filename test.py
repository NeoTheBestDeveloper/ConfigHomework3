import unittest

from main import Translator

class TestTranslator(unittest.TestCase):
    def test_global_constant(self):
        text = "global name = \"value\";"
        translator = Translator(text)
        xml_output = translator.translate()
        self.assertIn("<config><global name=\"name\">\"value\"</global></config>", xml_output)

    def test_array(self):
        text = "#(1, 2, 3)"
        translator = Translator(text)
        xml_output = translator.translate()
        self.assertIn("<array><value>1</value><value>2</value><value>3</value></array>", xml_output)

if __name__ == "__main__":
    unittest.main()