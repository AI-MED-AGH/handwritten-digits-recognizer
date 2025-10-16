extends ColorRect

signal clicked

const CLICKED_COLOR: Color = Color(0.184, 0.592, 0.157, 1.0)
const FADE_DURATION: float = 1.0

var _default_color: Color
var _color_tween: Tween
var _can_click: bool = true

@onready var _click_delay_timer: Timer = %ClickDelayTimer


func _ready() -> void:
	_default_color = color
	
	$Label.text = str(get_index())
	
	_click_delay_timer.timeout.connect(_on_click_delay_end)


func _gui_input(event: InputEvent) -> void:
	if not _can_click:
		return
	
	if event is InputEventMouseButton and event.pressed:
		_on_clicked()


func _on_clicked() -> void:
	_can_click = false
	_click_delay_timer.start()
	
	color = CLICKED_COLOR
	_color_tween = create_tween()
	_color_tween.tween_property(self, "color", _default_color, FADE_DURATION)

	clicked.emit()


func _on_click_delay_end() -> void:
	_can_click = true
