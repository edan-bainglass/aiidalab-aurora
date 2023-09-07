"""
Widget to setup tomato's settings
"""

from typing import Any, Dict

import ipywidgets as ipw
from aiida_aurora.schemas.dgbowl import Tomato_0p2
from aiida_aurora.schemas.utils import remove_empties_from_dict_decorator


class TomatoSettings(ipw.VBox):

    BOX_STYLE = {'description_width': 'initial'}
    BOX_LAYOUT = {'width': '95%'}
    BUTTON_STYLE = {'description_width': '30%'}
    BUTTON_LAYOUT = {'margin': '5px'}
    BOX_LAYOUT_2 = {
        'width': 'auto',
        'border': 'solid darkgrey 1px',
        'align_content': 'center',
        'padding': '5px'
    }

    def __init__(self, validate_callback_f):

        if not callable(validate_callback_f):
            raise TypeError(
                "validate_callback_f should be a callable function")

        # initialize job settings

        self.defaults: Dict[ipw.ValueWidget, Any] = {}

        self.w_job_header = ipw.HTML("<h2>Tomato Job configuration:</h2>")

        self.unlock_when_done = ipw.Checkbox(
            value=False,
            description="Unlock when done?",
        )
        self.defaults[self.unlock_when_done] = self.unlock_when_done.value

        self.verbosity = ipw.Dropdown(
            description="Verbosity:",
            value="INFO",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        self.defaults[self.verbosity] = self.verbosity.value

        self.w_monitor_header = ipw.HTML("<h2>Job Monitor configuration:</h2>")
        self.is_monitored = ipw.Checkbox(
            value=False,
            description="Monitored job?",
        )
        self.defaults[self.is_monitored] = self.is_monitored.value

        self.refresh_rate = ipw.BoundedIntText(
            description="Refresh rate (s):",
            min=10,
            max=1e99,
            step=1,
            value=600,
            style=self.BOX_STYLE,
        )
        self.defaults[self.refresh_rate] = self.refresh_rate.value

        self.check_type = ipw.Dropdown(
            description="Check type:",
            value="discharge_capacity",
            options=["discharge_capacity", "charge_capacity"],
        )
        self.defaults[self.check_type] = self.check_type.value

        self.threshold = ipw.BoundedFloatText(
            description="Threshold:",
            min=1e-6,
            max=1.0,
            value=0.80,
            style=self.BOX_STYLE,
        )
        self.defaults[self.threshold] = self.threshold.value

        self.consecutive = ipw.BoundedIntText(
            description="Number of consecutive cycles:",
            min=2,
            max=1e6,
            step=1,
            value=2,
            style=self.BOX_STYLE)
        self.defaults[self.consecutive] = self.consecutive.value

        self.w_monitor_parameters = ipw.VBox()

        self.w_job_calcjob_node_label = ipw.Text(
            description="AiiDA CalcJob node label:",
            placeholder="Enter a name for the BatteryCyclerExperiment node",
            layout={
                'width': 'auto',
                "margin": "5px 0",
            },
            style=self.BOX_STYLE)
        self.w_validate = ipw.Button(description="Validate",
                                     button_style='success',
                                     tooltip="Validate the settings",
                                     icon='check',
                                     style=self.BUTTON_STYLE,
                                     layout=self.BUTTON_LAYOUT)

        self.reset_button = ipw.Button(
            layout={},
            style={},
            description="Reset",
            button_style='danger',
            tooltip="Clear selection",
            icon='times',
        )

        # initialize widgets
        super().__init__()
        self.children = [
            self.w_job_header,
            ipw.VBox([self.unlock_when_done, self.verbosity],
                     layout=self.BOX_LAYOUT_2),
            self.w_monitor_header,
            ipw.VBox([self.is_monitored, self.w_monitor_parameters],
                     layout=self.BOX_LAYOUT_2),
            self.w_job_calcjob_node_label,
            ipw.HBox(
                layout={
                    "align_items": "center",
                },
                children=[
                    self.w_validate,
                    self.reset_button,
                ],
            ),
        ]

        # setup automations
        # job monitored checkbox
        self.is_monitored.observe(self._build_job_monitor_parameters,
                                  names="value")

        # validate protocol
        self.w_validate.on_click(
            lambda arg: self.callback_call(validate_callback_f))

        self.reset_button.on_click(self.reset)

        self.init()

    def init(self) -> None:
        """Initialize widget."""
        self._build_job_monitor_parameters()

    @property
    @remove_empties_from_dict_decorator
    def selected_monitor_settings(self):
        if self.is_monitored.value:
            return dict(
                refresh_rate=self.refresh_rate.value,
                check_type=self.check_type.value,
                threshold=self.threshold.value,
                consecutive_cycles=self.consecutive.value,
            )
        else:
            return {}

    @property
    @remove_empties_from_dict_decorator
    def selected_tomato_settings_dict(self):
        d = {
            'unlock_when_done': self.unlock_when_done.value,
            'verbosity': self.verbosity.value
        }
        if self.is_monitored.value:
            d['snapshot'] = {
                'frequency': self.refresh_rate.value,
                'prefix': 'snapshot'
            }
        return d

    @property
    def selected_tomato_settings(self):
        "The selected battery sample returned as a `aiida_aurora.schemas.dgbowl_schemas.Tomato_0p2` object."
        return Tomato_0p2.parse_obj(self.selected_tomato_settings_dict)

    @property
    def calcjob_node_label(self):
        return self.w_job_calcjob_node_label.value,

    def _build_job_monitor_parameters(self, dummy=None):
        if self.is_monitored.value:
            self.w_monitor_parameters.children = [
                self.refresh_rate,
                self.check_type,
                self.threshold,
                self.consecutive,
            ]
        else:
            self.w_monitor_parameters.children = []

    def reset_controls(self) -> None:
        """Reset controls and notices."""
        for control, value in self.defaults.items():
            control.value = value

    def reset(self, _=None) -> None:
        """Reset widget and registers."""
        self.reset_controls()

    def set_default_calcjob_node_label(self, sample_label, method_label):
        self.w_job_calcjob_node_label.value = f"{sample_label}-{method_label}"

    def callback_call(self, callback_function):
        "Call a callback function and this class instance to it."
        return callback_function(self)
