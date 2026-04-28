import json as js

from varname import nameof

from src.vk_api.types import ButtonTypes, ButtonColorTypes


class Button:
    def __init__(self, button_type: ButtonTypes, label: str = None,
                 payload: dict = None, link: str = None,
                 color: ButtonColorTypes = ButtonColorTypes.secondary):
        if not isinstance(button_type, ButtonTypes):
            raise TypeError(f"Argument '{nameof(button_type)}' must have a {ButtonTypes.__name__} type")
        if not isinstance(color, ButtonColorTypes):
            raise TypeError(f"Argument '{nameof(color)}' must have a {ButtonColorTypes.__name__} type")

        self.__type = button_type.value

        if label is None:
            raise TypeError(f"{self.__init__.__name__} missing 1 required positional argument: '{nameof(label)}'")
        elif not label:
            raise ValueError(f"{nameof(label)} won't be empty")
        if not isinstance(label, str):
            raise TypeError(f"Argument '{nameof(label)}' must have a {str.__name__} type")
        self.__label = label

        if self.__type == ButtonTypes.open_link:
            if link is None:
                raise TypeError(f"{self.__init__.__name__} missing 1 required positional argument: '{nameof(link)}'")
            elif not link:
                raise ValueError(f"{nameof(link)} won't be empty")
            if not isinstance(label, str):
                raise TypeError(f"Argument '{nameof(link)}' must have a {str.__name__} type")
            self.__link = link

        if not payload:
            self.__payload = {}
        else:
            self.__payload = payload

        self.__color = color.value

    @property
    def structure(self) -> dict:
        action_dict = dict()

        action_dict["type"] = self.__type
        action_dict["label"] = self.__label
        if self.__payload:
            action_dict["payload"] = self.__payload
        if self.__type == ButtonTypes.open_link:
            action_dict["link"] = self.__link

        structure = {"action": action_dict,
                     "color": self.__color}

        return structure

    @property
    def type(self):
        return self.__type

    @property
    def link(self):
        return self.__link

    @property
    def label(self):
        return self.__label

    @property
    def payload(self):
        return self.__payload

    @property
    def color(self):
        return self.__color

    def update_payload(self, keyword: str, value):
        self.__payload[keyword] = value


class Keyboard:
    def __init__(self, lines: list[list[Button]] = None, one_time: bool = False, inline: bool = False):
        if not lines:
            self.__lines = []
        else:
            self.__lines = lines
        self.__one_time = one_time
        self.__inline = inline

    def add_line(self, buttons: list[Button] = None):
        if buttons:
            self.__lines.append(buttons)

    def json(self) -> str:
        buttons_list = []
        if self.__lines:
            for line in self.__lines:
                buttons_in_line_list = []
                for button in line:
                    buttons_in_line_list.append(button.structure)
                buttons_list.append(buttons_in_line_list)
            keyboard_structure = {
                "one_time": self.__one_time,
                "inline": self.__inline,
                "buttons": buttons_list
            }
            return js.dumps(keyboard_structure, separators=(',', ':'))
        return ''
