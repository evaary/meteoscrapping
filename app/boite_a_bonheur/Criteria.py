class Criteria:

    def __init__(self, css_attr: str, attr_value: str):
        self.__css_attribute = css_attr
        self.__attribute_value = attr_value

    def get_css_attr(self):
        return self.__css_attribute

    def get_attr_value(self):
        return self.__attribute_value
