# vtasks is a curses Google Task client

import curses
import gtasks

# start the curses library, and return the screen
def start_curses( ):
  # create the curses screen
  screen = curses.initscr( )
  # don't spit input back
  curses.noecho( )
  # don't buffer input
  curses.cbreak( )
  # tell curses to parse special keys (eg arrows etc)
  screen.keypad(1)
  # turn off cursor
  curses.curs_set(0)
  # turn on color and return the screen
  curses.start_color( )
  curses.use_default_colors( )
  return screen

# shut down curses
def stop_curses(screen):
  curses.nocbreak()
  screen.keypad(0)
  curses.echo()
  curses.endwin()

# returns a color pair for the status line
def get_status_color( ):
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
  return curses.color_pair(1)

# draw the interface of the program
def draw_window(screen):
  # draw the header bar
  current_line = 1
  (cols, rows) = screen.getmaxyx( )
  screen.addstr(0, 0, "q:Quit n:New e:Edit c:Check ?:Help".ljust(rows), get_status_color( ))
  # for each task list they have
  for item in gtasks.get_tasks( ):
    screen.addstr(current_line, 0, item)
    current_line += 1
  # draw the footer bar
  screen.addstr(cols - 1, 0, "vtasks: Research".ljust(rows - 1), get_status_color( ))

# the main program loop
def main_loop(screen):
  while True:
    draw_window(screen)
    c = screen.getch( )
    if c == ord('q'):
      return

# main function which is called after authenticating the application
def main( ):
  screen = start_curses( )
  main_loop(screen)
  stop_curses(screen)

# when run as a script
if __name__ == "__main__":
  # call the authenticate function which will do the Google authentication
  # and then call the main function above in a try/catch block for us
  gtasks.authenticate( )

