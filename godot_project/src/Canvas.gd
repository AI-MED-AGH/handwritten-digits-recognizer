extends ColorRect

signal redrawed(Image)

@export var pen_color = Color(1, 1, 0)
@export_range(1, 50) var pen_size: float = 5
@export_range(1, 10) var pen_delay: float = 1

@onready var viewport = SubViewport.new()
@onready var board = TextureRect.new()
@onready var pen: Line2D
@onready var pen2: Line2D
@onready var redrawed_timer = Timer.new()

var mouse_pos = Vector2()
var tex : Image

var _is_dragging: bool = false


func _ready():
	viewport.set_size(size)
	viewport.set_clear_mode(SubViewport.ClearMode.CLEAR_MODE_ALWAYS)
	viewport.set_transparent_background(true)

	_new_pen()
	
	# Use a sprite to display the result texture
	board.set_texture(viewport.get_texture())

	redrawed_timer.wait_time = 0.2
	redrawed_timer.one_shot = true
	redrawed_timer.autostart = false
	redrawed_timer.timeout.connect(_emit_redrawed_signal_for_frame)

	add_child(viewport)
	add_child(board)
	add_child(redrawed_timer)


func _new_pen() -> void:
	pen = Line2D.new()
	pen.set_joint_mode(Line2D.LINE_JOINT_ROUND)
	pen.set_begin_cap_mode(Line2D.LINE_CAP_ROUND)
	pen.set_end_cap_mode(Line2D.LINE_CAP_ROUND)
	pen.set_default_color(pen_color)
	pen.set_antialiased(true)
	pen.set_width(pen_size)
	
	pen2 = pen.duplicate()
	var sub_pen_color = pen_color
	sub_pen_color.a = 1
	pen2.set_default_color(sub_pen_color)
	pen2.set_width(pen_size * 0.5)
	
	viewport.add_child(pen)
	viewport.add_child(pen2)


func clear_viewport() -> void:
	for c in viewport.get_children():
		c.queue_free()
	
	#viewport.set_clear_mode(SubViewport.ClearMode.CLEAR_MODE_ONCE)
	_emit_redrawed_signal_for_frame()
	
	_new_pen()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch or event is InputEventMouseButton:
		if event.pressed:
			_is_dragging = true
			_draw_at_mouse()
			_draw_at_mouse()
		else:
			_new_pen()
			_is_dragging = false
	
	if event is InputEventScreenDrag or (event is InputEventMouseMotion and _is_dragging):
		#if event.relative.length() > pen_delay:
		_draw_at_mouse()


func _draw_at_mouse() -> void:
	mouse_pos = get_local_mouse_position()
	pen.add_point(mouse_pos)
	pen2.add_point(mouse_pos)
	
	if redrawed_timer.is_stopped():
		redrawed_timer.start()


func _emit_redrawed_signal_for_frame() -> void:
	await RenderingServer.frame_post_draw
	var texture = viewport.get_texture()
	var image = texture.get_image()
	redrawed.emit(image)
