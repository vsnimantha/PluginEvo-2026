class ParameterInfo:
    def __init__(self, data_type_block,data_type, identifier_block, identifier_value,data_value,param_code):
        self.data_type_block = data_type_block
        self.data_type_value = data_type
        self.identifier_block = identifier_block
        self.identifier_value = identifier_value
        self.data_value=data_value
        self.param_code=param_code

    def __str__(self):
        return (
            f"ParameterInfo:\n"
            f"  • Data Type Block: {self.data_type_block}\n"
            f"  • Data Type Value: {self.data_type_value}\n"
            f"  • Identifier Block: {self.identifier_block}\n"
            f"  • Identifier Value: {self.identifier_value}\n"
            f"  • Data Value: {self.data_value}\n"
            f"  • Param Code: {self.param_code}"
        )
