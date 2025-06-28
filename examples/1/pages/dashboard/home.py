from flet import * 
from fletx import FletX
from fletx.core import FletXPage
from fletx.navigation import navigate, go_back

from .controller import DashboardController
from ..shared.components import (
    TaskComponent
)

class DashboardHomePage(FletXPage):
    def __init__(self):
        self.controller = FletX.find(DashboardController) or DashboardController()
        super().__init__(
            enable_keyboard_shortcuts = True
        )

    def _safe_refresh(self):
        """safe refresh"""
        print('refreshing..........................')
        if not hasattr(self, '_refreshing'):
            self._refreshing = True
            self.controller.load_data()
            del self._refreshing
    
    def on_init(self):
        # Charge les données quand la page est montée
        self.controller.load_data()
        self.add_keyboard_shortcut("ctrl+r", lambda: print('ctrl+r................activated\n'), "Refresh page")
        self.add_keyboard_shortcut("ctrl+d", lambda: print('ctrl+d................activated\n'), "Refresh page")
        # self._setup_built_in_handlers()
        # self.page.on_keyboard_event = lambda e: print('Key pressed:',e)
        
    def build(self):
        # Initialisation sécurisée
        if not hasattr(self, '_built'):  # Protection contre les appels multiples
            self.controller.initialize()
            self._built = True
            
            return SafeArea(
                expand = True,
                minimum_padding = padding.symmetric(vertical=12),

                content = Column(
                    expand = True,
                    alignment = MainAxisAlignment.START,
                    scroll = ScrollMode.AUTO,
                    spacing = 20,

                    controls = [
                        Container(
                            height = 0
                        ),
                        Container(
                            padding = padding.symmetric(horizontal=8, vertical=4),
                            content = Column(
                                expand = True,
                                controls = [
                                    # Header with User Avatar and Logout Button
                                    Row(
                                        alignment = MainAxisAlignment.SPACE_BETWEEN,
                                        controls = [
                                            # Content with IconButton
                                            IconButton(
                                                icon = Icons.ARROW_BACK_IOS,
                                                bgcolor = Colors.BLACK45,
                                                icon_color = Colors.WHITE,
                                                on_click = lambda _: go_back()

                                                # style

                                            ),
                                            
                                            # User Avatar
                                            CircleAvatar(
                                                foreground_image_src = 'images/dev1.jpg',
                                                radius = 24,
                                            ),
                                        ]
                                    ),

                                    # Divider
                                    Container(
                                        height = 10
                                    ),

                                    # Welcome TEXT
                                    Text(
                                        f"What are you doing today {self.controller.username}?",
                                        style = TextStyle(
                                            size = 20,
                                            weight = FontWeight.W_400
                                        )
                                    ),

                                    # Search Bar
                                    TextField(
                                        hint_text = "Search...",
                                        prefix_icon = Icons.SEARCH,
                                        border = InputBorder.NONE,
                                        filled = True,
                                        # fill_color = Colors.GREY_900,
                                        fill_color = Colors.with_opacity(
                                            color = Colors.GREY_900,
                                            opacity = .5
                                        ),
                                        border_radius = BorderRadius(
                                            top_left = 30, 
                                            top_right = 8, 
                                            bottom_left = 8, 
                                            bottom_right = 8
                                        ),
                                        focused_border_color = Colors.TRANSPARENT,
                                        hover_color = Colors.with_opacity(
                                            color = Colors.GREY_900,
                                            opacity = .55
                                        ),
                                        content_padding = padding.symmetric(horizontal=16, vertical=8),
                                        on_submit = self._safe_refresh
                                    ),
                                ]
                            ),
                        ),
                        
                        # Categories
                        Column(
                            expand = True,
                            spacing = 2,
                            controls = [
                                # Categories Header
                                Container(
                                    padding = padding.symmetric(horizontal=8, vertical=4),
                                    content = Row(
                                        alignment = MainAxisAlignment.SPACE_BETWEEN,
                                        controls = [
                                            Text(
                                                "CATEGORIES",
                                                style = TextStyle(
                                                    size = 14,
                                                    weight = FontWeight.W_400,
                                                    color = Colors.GREY_500
                                                )
                                            ),
                                            ElevatedButton(
                                                text = "See all",
                                                on_click = lambda e: navigate("/categories")
                                            )
                                        ]
                                    )
                                ),

                                # Categories List
                                Container(
                                    expand = True,
                                    padding = padding.symmetric(horizontal=0, vertical=4),
                                    height = 110,
                                    content = ListView(
                                        expand = True,
                                        auto_scroll = True,
                                        horizontal = True,
                                        spacing = 20,
                                        controls = [
                                            Container(
                                                width = 170,
                                                height = 110,
                                                bgcolor = Colors.with_opacity(
                                                    color = Colors.GREY_900, 
                                                    opacity = .5
                                                ),
                                                clip_behavior = ClipBehavior.NONE,
                                                padding = padding.all(10),
                                                border_radius = 20,
                                                content = Column(
                                                    expand = True,
                                                    alignment = MainAxisAlignment.CENTER,
                                                    spacing = 10,
                                                    controls = [
                                                        Text(
                                                            f"{i * 10} Tasks",
                                                            style = TextStyle(
                                                                size = 12,
                                                                weight = FontWeight.W_400,
                                                                color = Colors.GREY_500
                                                            )
                                                        ),
                                                        Text(
                                                            f"Category {i + 1}",
                                                            style = TextStyle(
                                                                size = 16,
                                                                weight = FontWeight.W_500,
                                                                color = Colors.WHITE
                                                            )
                                                        ),
                                                        # Progress Bar
                                                        ProgressBar (
                                                            value = i / 5,  # Simulated progress
                                                            # stroke_width = 4,
                                                            color = Colors.BLUE_800 if i % 2 == 0 else Colors.PINK_600,
                                                        )
                                                    ]
                                                )
                                            ) for i in range(5)
                                        ]
                                    )
                                ),

                                # Divider
                                Container(
                                    height = 5
                                ),

                                # Tasks Section
                                Container(
                                    padding = padding.symmetric(horizontal=8, vertical=4),
                                    content = Row(
                                        alignment = MainAxisAlignment.SPACE_BETWEEN,
                                        controls = [
                                            Text(
                                                "TASKS",
                                                style = TextStyle(
                                                    size = 14,
                                                    weight = FontWeight.W_400,
                                                    color = Colors.GREY_500
                                                )
                                            ),
                                            ElevatedButton(
                                                text = "See all",
                                                on_click = lambda e: navigate("/tasks")
                                            )
                                        ]
                                    )
                                ),

                                # Tasks List
                                Container(
                                    expand = True,
                                    padding = padding.symmetric(horizontal=0, vertical=4),
                                    # height = 200,
                                    content = ListView(
                                        expand = True,
                                        auto_scroll = True,
                                        spacing = 10,
                                        controls = [
                                            TaskComponent(
                                                index = idx + 1,
                                                task_id = task.get(
                                                    'task_id', f'task-{idx + 1}'
                                                ),
                                                task_name = task.get(
                                                    'task_name', f"Task {idx + 1}"
                                                )                                            
                                            )
                                            for idx, task in enumerate(self.controller.todos)
                                        ]
                                    )
                                )
                            ]
                        ),
                    ]
                )
            ) 
        
        return ProgressRing()  # Fallback UI
    