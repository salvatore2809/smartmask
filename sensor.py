class Sensor:
    sensor_name = ""
    value_unit_of_measure = ""
    get_value_instruction = ""
    number_of_axis = 1
    offset = 0
    current_value = 0
    def __init__(self,sensor_name, um, get_value_instruction, number_of_axis = 1, offset = 0, precision = 2):
        self.sensor_name = sensor_name
        self.value_unit_of_measure ='[' + um + ']'
        self.get_value_instruction = get_value_instruction
        self.number_of_axis = number_of_axis
        self.offset = offset
        self.value_precision = str(precision)
        if self.number_of_axis == 1 :
            self.format_str = str("{:."+ self.value_precision +"f}")
        if self.number_of_axis == 3 :
            self.format_str = str("{0:."+self.value_precision+"f}; {1:."+self.value_precision+"f}; {2:."+self.value_precision+"f}")
    def get_sensor_value(self):
        self.current_value = eval(self.get_value_instruction)
        return self.current_value
    def get_label(self):
        return self.sensor_name + self.value_unit_of_measure
    def get_sensor_value_string(self):
        if self.number_of_axis == 1 :
            return self.format_str.format(self.get_sensor_value() + self.offset)
        if self.number_of_axis == 3 :
            x,y,z = self.get_sensor_value()
            return self.format_str.format(x + self.offset, y + self.offset, z + self.offset)
