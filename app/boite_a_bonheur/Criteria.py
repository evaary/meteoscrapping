class Criteria:

    def __init__(self, css_attr: str, attr_value: str):
        self._css_attribute = css_attr
        self._attribute_value = attr_value

    @property
    def css_attribute(self):
        return self._css_attribute

    @property
    def attribute_value(self):
        return self._attribute_value

    def __repr__(self):
        return f"{self._css_attribute} : {self._attribute_value}"

    def __copy__(self):
        return Criteria(self._css_attribute, self._attribute_value)
