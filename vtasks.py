# vtasks, a terminal google tasks client, MIT license
# this file includes the curses interface

from os import system
from random import choice
import curses
import curses.textpad
import gtasks
from string import ascii_uppercase, digits

# global to keep track of tasks it is updated
# from goole (via the gtasks.get_tasks( ) function
# as needed
tasks = None

# the status message to show.  It is displayed until
# the user hits a key at which point it is cleared
status = ""

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

# return a new temporary file name
# this is done with a fixed prefix + 8 random letters and digits
# this makes it likely that we will use different files for different
# tasks meanging the user can see his task files if he needs to for some
# reason (this has proved useful with mutt)
def get_tmp_file( ):
  return "/tmp/vtasks-" + "".join(choice(ascii_uppercase + digits) for _ in range(8))


# create a new task and enter it into the task list
def new_task( ):
  global tasks
  # get the temp file name
  fname = get_tmp_file( )
  # suspend curses before we execute the editor
  curses.endwin( )
  # next we open this file with the user's $EDITOR
  system("$EDITOR " + fname)
  # when this returns, the file we created should be filled with the users task
  # resume curses
  screen = curses.initscr( )
  screen.refresh( )
  curses.doupdate( )
  # add the task in this file
  gtasks.add_task(fname)
  # refresh the task list
  tasks = gtasks.get_tasks( )

# edits an existing task
def edit_task(which):
  global tasks
  # get the temp file name
  fname = get_tmp_file( )
  # write the task into this file
  tasks[which].write_file(fname)
  # open an editor on the file
  curses.endwin( )
  # next we open this file with the user's $EDITOR
  system("$EDITOR " + fname)
  # when this returns, the file we created should be filled with the users task
  # resume curses
  screen = curses.initscr( )
  screen.refresh( )
  curses.doupdate( )
  # we update the task by deleting it and adding a fresh one with the new data
  tasks[which].delete( )
  gtasks.add_task(fname)
  # refresh the task list
  tasks = gtasks.get_tasks( )





# returns a color pair for the header line
def get_header_color( ):
  curses.init_pair(1, -1, curses.COLOR_BLACK)
  return curses.color_pair(1)

# get a color pair for completed tasks
def get_completed_color( ):
  curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
  return curses.color_pair(2) | curses.A_BOLD

# returns a color pair for the current highlighted line
def get_highlight_color( ):
  curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
  return curses.color_pair(3) | curses.A_BOLD

# returns a color pair for when we are highlighted AND completed
def get_completed_highlight_color( ):
  curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
  return curses.color_pair(4) | curses.A_BOLD

# retutn a color pair for the status message at the bottom
def get_status_color( ):
  curses.init_pair(5, curses.COLOR_RED, -1)
  return curses.color_pair(5)

# draw a task to the screen
def draw_task(screen, task, i, highlight, rows):
  # set the style up
  if task.completed( ) and i == highlight:
    style = get_completed_highlight_color( )
  elif task.completed( ):
    style = get_completed_color( )
  elif i == highlight:
    style = get_highlight_color( )
  else:
    style = curses.A_BOLD
  # set up the text to be shown
  line = ' ' + str(i).ljust(4) + task.due( ).ljust(8) + task.text( )
  if len(line) < rows:
    line = line.ljust(rows)
  # draw it
  screen.addstr(i, 0, line, style)

# get user text from a little widget and return it
def get_user_text(screen, message, first):
  (cols, rows) = screen.getmaxyx( )
  nw = curses.newwin(1, rows - 1, cols - 1, 0)
  tb = curses.textpad.Textbox(nw)
  for c in message + ": " + chr(first):
    tb.do_command(c)
  text = tb.edit( )
  return text[len(message) + 2:]

# draw the interface of the program
def draw_window(screen, highlight):
  global tasks
  global status
  # draw the header bar
  i = 1
  (cols, rows) = screen.getmaxyx( )
  screen.addstr(0, 0, "q:Quit n:New e:Edit d:Delete c:Clear ?:Help".ljust(rows), get_header_color( ))
  # get tasks if needed
  if tasks == None:
    tasks = gtasks.get_tasks( )
  # for each task list they have
  for item in tasks:
    draw_task(screen, item, i, highlight, rows)
    i += 1
  # draw the status message (may be empty string)
  screen.addstr(cols - 1, 0, status.ljust(rows - 1), get_status_color( ))

# the main program loop
def main_loop(screen):
  global tasks
  global status
  highlight = 1
  while True:
    # clear and redraw the screen, then wait for input
    screen.clear( )
    draw_window(screen, highlight)
    c = screen.getch( )
    # clear any old status message
    status = ""
    # quit
    if c == ord('q'):
      return
    # scrolling down
    elif c == ord('j') or c == curses.KEY_DOWN:
      highlight += 1
      if highlight > len(tasks):
        highlight -= 1
    # scrolling up
    elif c == ord('k') or c == curses.KEY_UP:
      highlight -= 1
      if highlight < 1:
        highlight += 1
    # check/uncheck a task
    elif c == ord('d'):
      tasks[highlight - 1].check( )
      tasks = gtasks.get_tasks( )
    # clear all checked tasks
    elif c == ord('c'):
      for task in tasks:
        if task.completed( ):
          task.delete( )
      tasks = gtasks.get_tasks( )
    # make a new task
    elif c == ord('n'):
      new_task( )      
    # edit the existing task
    elif c == ord('e'):
      edit_task(highlight - 1)
    # jump to task by number
    elif c >= ord('0') and c <= ord('9'):
      # get the whole number
      num = get_user_text(screen, "Jump to task", c)
      try:
         num = int(num)
         if num < 1:
           raise ValueError
         elif num > len(tasks):
           raise ValueError
         highlight = num
      except ValueError:
        status = "Invalid number"

      



# main function which is called after authenticating the application
def main( ):
  screen = start_curses( )
  main_loop(screen)
  stop_curses(screen)

# when run as a script run our main function
if __name__ == "__main__":
  main( )

