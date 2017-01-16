import os
import random
from settings import magic_word, programs_pwd

class TweetProcessor:
  def __init__ (self, state, text, author):
    if state == None:
      state = {"blocked" : False}
    self.cfg = state
    self.is_query = False
    self.blocked = state["blocked"]
    self.is_query = False
    self.recipients = ["@"+author]
    self.filter_names = []

    for e in text.split():
      if e == magic_word:
        self.is_query = True
        continue

      if e[0] == "@":
        self.recipients.append(e)
        continue

      self.filter_names.append(e)
    self.recipients = list(set(self.recipients))

  def response(self): # response text for a tweet
    return " ".join(self.recipients)

  def generate_image(self, tgt_path, src_path):
    commands = {
#      "nothing" : "cp",      # for debug only
      "hilbert" : str(programs_pwd/"hilbert_path"),
      "voronoi" : str(programs_pwd/"voronoi"),
      "abstract_voronoi" : str(programs_pwd/"voronoi_lowres"),
      "enhance" : str(programs_pwd/"mid_color"),
      "black_and_white" : str(programs_pwd/"mid_grayscale"),
    }

    command = random.choice(list(commands.values()))

    for filter_name in self.filter_names:
      if filter_name in commands:
        command = commands[filter_name]

    os.system("jpegtran {} >tmp.jpg".format(src_path))
    os.system("mv tmp.jpg {}".format(src_path))
    print("{} {} {}".format(command, src_path, tgt_path))
    os.system("{} {} {}".format(command, src_path, tgt_path))

  def should_process(self):
    return self.is_query

  def updated_config(self):
    return self.cfg
