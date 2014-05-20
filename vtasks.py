# vtasks is a curses Google Task client

import curses
import gtasks

# global to keep track of tasks
tasks = None

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

# returns a color pair for the current highlighted line
def get_highlight_color( ):
  curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
  return curses.color_pair(2) | curses.A_BOLD

def draw_task(screen, task, i, highlight, rows):
  if i == highlight:
    screen.addstr(i, 0, task[1].ljust(rows), get_highlight_color( ))
  else:
    screen.addstr(i, 0, task[1].ljust(rows), curses.A_BOLD)

# draw the interface of the program
def draw_window(screen, highlight):
  global tasks
  # draw the header bar
  i = 1
  (cols, rows) = screen.getmaxyx( )
  screen.addstr(0, 0, "q:Quit n:New e:Edit c:Check ?:Help".ljust(rows), get_status_color( ))
  # get tasks if needed
  if tasks == None:
    tasks = gtasks.get_tasks( )

  # for each task list they have
  for item in tasks:
    draw_task(screen, item, i, highlight, rows)
    i += 1
  # draw the footer bar
  screen.addstr(cols - 1, 0, "vtasks: Research".ljust(rows - 1), get_status_color( ))

# the main program loop
def main_loop(screen):
  highlight = 1
  while True:
    draw_window(screen, highlight)
    c = screen.getch( )
    if c == ord('q'):
      return
    elif c == ord('j'):
      highlight += 1
    elif c == ord('k'):
      highlight -= 1

# main function which is called after authenticating the application
def main( ):
  screen = start_curses( )
  main_loop(screen)
  stop_curses(screen)

# when run as a script run our main function
if __name__ == "__main__":
  main( )

