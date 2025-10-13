extends TextureRect

signal redrawed(Image)

@export var pen_color = Color(1, 1, 0)
@export_range(0.1, 50) var pen_radius: float = 5
@export var margin_at_each_side: int = 0

@onready var viewport = SubViewport.new()
@onready var board = TextureRect.new()
@onready var pen: Line2D
@onready var pen2: Line2D
@onready var redrawed_timer = Timer.new()

var last_draw_pos = Vector2()
var image : Image

var _is_dragging: bool = false


func _ready():
	var img_size = Vector2i(28 - margin_at_each_side*2, 28 - margin_at_each_side*2)
	image = Image.create_empty(img_size.x, img_size.y, false, Image.Format.FORMAT_L8)
	_update_texture_image()

	custom_minimum_size = img_size
	size = img_size
	get_parent().custom_minimum_size = custom_minimum_size * scale

	redrawed_timer.wait_time = 0.2
	redrawed_timer.one_shot = false
	redrawed_timer.autostart = true
	redrawed_timer.timeout.connect(_emit_redrawed_signal_for_frame)

	add_child(viewport)
	add_child(board)
	add_child(redrawed_timer)


func _update_texture_image() -> void:
	texture = ImageTexture.create_from_image(image)


func paint_dot_brush(pos: Vector2) -> void:
	for dx in range(-pen_radius, pen_radius + 1):
		for dy in range(-pen_radius, pen_radius + 1):
			var px = pos.x + dx
			var py = pos.y + dy
			if px < 0 or py < 0 or px >= image.get_width() or py >= image.get_height():
				continue
			var dist = sqrt(dx * dx + dy * dy)
			if dist > pen_radius:
				continue
			var alpha = clamp(1.0 - dist / pen_radius, 0, 1)
			var existing_color = image.get_pixel(px, py)
			var new_color = existing_color.lerp(pen_color, alpha * pen_color.a)
			image.set_pixel(int(px), int(py), new_color)


# New function to draw a line by painting dots along it
func paint_line_brush(pos1: Vector2, pos2: Vector2) -> void:
	var dist = Vector2(pos2.x - pos1.x, pos2.y - pos1.y).length()
	var steps = int(dist)
	if steps == 0:
		paint_dot_brush(pos1)
		_update_texture_image()
		return
	for i in range(steps + 1):
		var t = float(i) / steps
		var interp_pos = lerp(pos1, pos2, t)
		paint_dot_brush(interp_pos)

	_update_texture_image()

func clear_viewport() -> void:
	image.fill(Color.BLACK)
	_update_texture_image()
	_emit_redrawed_signal_for_frame()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch or event is InputEventMouseButton:
		if event.pressed:
			_is_dragging = true
			last_draw_pos = get_local_mouse_position()
			_draw_at_mouse()
		else:
			_is_dragging = false
			_emit_redrawed_signal_for_frame()
	
	if event is InputEventScreenDrag or (event is InputEventMouseMotion and _is_dragging):
		_draw_at_mouse()


func _draw_at_mouse() -> void:
	var mouse_pos = get_local_mouse_position()
	
	paint_line_brush(last_draw_pos, mouse_pos)
	
	last_draw_pos = mouse_pos
	
	#if redrawed_timer.is_stopped():
		#redrawed_timer.start()


func _emit_redrawed_signal_for_frame() -> void:
	var img_with_margins = Image.create_empty(28, 28, false, Image.Format.FORMAT_L8)
	
	for y in range(margin_at_each_side, 28-margin_at_each_side):
		for x in range(margin_at_each_side, 28-margin_at_each_side):
			img_with_margins.set_pixel(x, y, image.get_pixel(x-margin_at_each_side, y-margin_at_each_side))
			
	redrawed.emit(img_with_margins)
