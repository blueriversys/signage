import pygame
import pygame.freetype  # Import the freetype module.
import time

class Color:
    black = 0, 0, 0
    white = 255, 255, 255
    red = 255, 0, 0
    green = 0, 255, 0
    blue = 0, 0, 255

class Display:
    FULLSCREEN = 0
    WINDOW = 1

    def __init__(self, mode=FULLSCREEN, screen_size=(800,600)):
        # Initialize pygame and display a blank screen.
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        if mode == Display.FULLSCREEN:
            self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
        else:
            self._screen = pygame.display.set_mode(screen_size)
        self._size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self._bgcolor = Color.black
        self._fgcolor = Color.blue
        self._small_font = pygame.font.Font(None, 50)
        self._big_font = pygame.font.Font(None, 250)

    def set_background_color(self, color):
        self._bgcolor = color

    def set_foreground_color(self, color):
        self._fgcolor = color

    def get_display_size(self):
        pass

    def get_screen_size(self):
        return self._screen.get_size()

    def render_text(self, message, font_size=None, color=Color.white):
        """Draw the provided message and return as pygame surface of it rendered
        with the configured foreground and background color.
        """
        # Default to small font if not provided.
        if font_size is None:
            font = self._small_font
        else:
            font = pygame.font.Font(None, font_size)
        return font.render(message, True, color, self._bgcolor)

    def print_text(self, text, font_size):
        self.print_color_text(text, font_size, self.white)

    def print_color_text(self, message, font_size, color=Color.white):
        txt = self.render_text(message, font_size, color)
        self._screen.fill(self._bgcolor)
        sw, sh = self._screen.get_size()
        lw, lh = txt.get_size()
        self._screen.blit(txt, (round(sw / 2 - lw / 2), round(sh / 2 - lh / 2)))
        pygame.display.update()

    def print(self, x, y, message):
        txt = self.render_text(message)
        self._screen.blit(txt, (x, y))
        pygame.display.update()

    def print_line(self, y, message, font_size, color=Color.white):
        txt = self.render_text(message, font_size, color)
        w, h = txt.get_size()
        sw, sh = self._screen.get_size()
        x = (sw - w) / 2
        self._screen.blit(txt, (x, y))
        pygame.display.update()

    def print_countdown(self, message, font_size, seconds=3):
        countdown_time = seconds
        label1 = self.render_text(message, font_size, Color.blue)
        l1w, l1h = label1.get_size()
        sw, sh = self._screen.get_size()
        y = round(sh / 2 - l1h)
        self._screen.blit(label1, (round(sw / 2 - l1w / 2), y))
        for i in range(countdown_time, 0, -1):
            # Each iteration of the countdown rendering changing text.
            label2 = self.render_text(str(i), font_size*2)
            l2w, l2h = label2.get_size()
            # Clear screen and draw text with line1 above line2 and all
            # centered horizontally and vertically.
            space_surface = self.render_text("    ", font_size*2)
            x1, y1 =  round((sw - l2w) / 2), (y + l1h)
            self._screen.blit(space_surface, (x1-40, y1))
            self._screen.blit(label2, (x1,y1))
            pygame.display.update()
            # Pause for a second between each frame.
            time.sleep(1)

    def print_countup(self, message, font_size, seconds=3):
        label1 = self.render_text(message, font_size, Color.blue)
        l1w, l1h = label1.get_size()
        sw, sh = self._screen.get_size()
        i = 0
        while True:
            i += 1
            # Each iteration of the countdown rendering changing text.
            label2 = self.render_text(str(i), font_size*2)
            l2w, l2h = label2.get_size()
            # Clear screen and draw text with line1 above line2 and all
            # centered horizontally and vertically.
            self._screen.fill(self._bgcolor)
            self._screen.blit(label1, (round(sw / 2 - l1w / 2), round(sh / 2 - l2h / 2 - l1h)))
            self._screen.blit(label2, (round(sw / 2 - l2w / 2), round(sh / 2 - l2h / 2)))
            pygame.display.update()
            # Pause for a second between each frame.
            time.sleep(1)

    def quit(self):
        pygame.display.quit()
        pygame.quit()
'''
#Test area, which can be deleted later
display = Display(mode=Display.WINDOW)
print(f'Display size: {display.get_display_size()}')
display.print_line(50, "This is a x y message")
time.sleep(5)

print(f'Display size: {display.get_display_size()}')
display.set_background_color(Color.green)
display.print_color_text("a message to print", 100, Color.white)
time.sleep(2)
display.print_countdown("Countdown in default seconds: ", 100)
display.print_countdown("Starting playback in seconds: ", 100, 6)
display.print_countup("This will count up", 40)
'''
