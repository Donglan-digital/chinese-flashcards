from tkinter import *
from tkinter import PhotoImage
from tkinter import messagebox
import pandas
from deep_translator import GoogleTranslator
import os
import re

# ------Constants------#
FONT_NAME = "Ariel"
BACKGROUND_COLOR = "#FC926E"
current_card = {}
flip_timer = None
current_index = 0  # Add an index to keep track of the current word
#-----generate user word list------#

def user_word():
    """Get user input of multiple Chinese words, translate each, and save to a file."""
    chinese_words = user_word_input.get().strip()  # Get input and remove extra spaces

    if chinese_words:  # Ensure input is not empty
        # Split using space (" "), comma (","), or Chinese comma ("，")
        words_list = [word.strip() for word in re.split(r"[ ,，]+", chinese_words) if word]
        translations = [{"Chinese": word, "English": GoogleTranslator(source="zh-CN", target="en").translate(word)}
                        for word in words_list]  # Translate each word and formate them into Chinese, English

        # Save translations to file
        data = pandas.DataFrame(translations)
        # Append to CSV file (create if not exists)
        if not os.path.exists("data/chinese_words.csv"):  # Create file with headers if it doesn’t exist
            data.to_csv("data/chinese_words.csv", index=False)
        else:  # Append without writing headers again
            data.to_csv("data/chinese_words.csv", mode="a", index=False, header=False)

        user_word_input.delete(0, END)  # Clear input field

#------generate new words------#
try:
    word_data = pandas.read_csv("data/chinese_words.csv")
    full_word_list = word_data.to_dict(orient="records")
except (FileNotFoundError, pandas.errors.EmptyDataError):
    full_word_list = []  # Ensure it's not empty

def generate_new_word ():
    global current_card, flip_timer, current_index
    if not full_word_list:  # Check if list is empty
        canvas.itemconfig(language_text, text="No words found!", fill="red")
        return
    if flip_timer:
        window.after_cancel(flip_timer)
        # Check if we've looped through all the words

    if current_index >= len(full_word_list):
        # Update the labels when all words are done
        canvas.itemconfig(language_text, text="That's all for today.", fill="green")
        canvas.itemconfig(word_text, text="Keep learning!", fill="green")
        # Wait for 3 seconds, then show the message box
        window.after(3000, show_words_to_learn)  # Use after to avoid blocking the main loop
        return
        # Get the current word using the current index and update the current card
    current_card = full_word_list[current_index]

    # Update UI elements
    canvas.itemconfig(language_text, text="Chinese 中文", fill="black")
    canvas.itemconfig(word_text, text=current_card["Chinese"], fill="black")
    canvas.itemconfig(canvas_image, image=card_front_image)
    ready_button.destroy()

    # Set the timer for flipping to English
    flip_timer = window.after(5000, flip_to_english)

    # Update the index for the next word
    current_index += 1

#------flip the card------#

def flip_to_english ():
    canvas.itemconfig(canvas_image, image = card_back_image)
    canvas.itemconfig(language_text, text="English", fill="navy")
    canvas.itemconfig(word_text, text=current_card["English"], fill="navy")

#------save words to learn------#
def save_to_learn_words():
    """Save the current word to 'words_to_learn.txt' when user clicks 'I'm learning this word'."""
    if current_card:  # Ensure there's a word being displayed
        with open("data/words_to_learn.txt", "a", encoding="utf-8") as file:
            file.write(f"{current_card['Chinese']},{current_card['English']}\n")

#------show word to learn to user------#
def show_words_to_learn():
    # Read all the words from 'words_to_learn.txt'
    if os.path.exists("data/words_to_learn.txt"):
        with open("data/words_to_learn.txt", "r", encoding="utf-8") as file:
            words = file.readlines()

        # Prepare the list of words
        words_list = "".join(words)

        # Show the message box with the list of words
        messagebox.showinfo("Words to Learn", f"Here are the words to learn:\n\n{words_list}")

# ------UI------ #
window = Tk()
window.title("Chinese Words 中文词语")
window.config(padx=30, pady=30, bg=BACKGROUND_COLOR)

canvas = Canvas(width=512,height=512, highlightthickness=0)
card_back_image = PhotoImage(file="images/card_back.png")
card_front_image = PhotoImage(file="images/card_front.png")
canvas_image = canvas.create_image(256,256, image=card_front_image)
language_text = canvas.create_text(256, 100, text="Are you ready?", fill="black", font=(FONT_NAME, 20, "italic"))
word_text = canvas.create_text(256, 256, text="Explain the words in English", fill="black", font=(FONT_NAME, 25, "bold"))
canvas.grid(column=1, row=1, columnspan=2)

user_word_input = Entry(width=45)
user_word_input.grid(column=1, row=0)
user_word_button = Button (text="Generate a Chinese word list", highlightthickness=0, command=user_word)
user_word_button.grid(column=2, row=0)

ready_button = Button(text="Go", highlightthickness=0, command=generate_new_word)
ready_button.place(x=400, y=112)

to_learn_button = Button(text="I'm learning this word.", highlightthickness=0, command=save_to_learn_words)
to_learn_button.grid(column=1, row=3)

next_button = Button(text="Next word.", highlightthickness=0, command=generate_new_word)
next_button.grid(column=2, row=3)


window.mainloop()
