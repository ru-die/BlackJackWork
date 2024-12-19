import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Глобальные переменные
suits = ["♥", "♦", "♣", "♠"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
deck = [(rank, suit) for suit in suits for rank in ranks]
player_hand = []
dealer_hand = []
player_score = 0
dealer_score = 0
player_balance = 1000 # Начальный баланс
bet_amount = 0

player_cards = [] # Список виджетов карт игрока
dealer_cards = [] # Список виджетов карт дилера

def create_deck():
    global deck
    deck = [(rank, suit) for suit in suits for rank in ranks] # Пересоздаем колоду

def deal_card(hand, hidden=False):
    global deck
    if not deck: # Проверяем, пуста ли колода, и если да - создаем новую
        create_deck()
        random.shuffle(deck)
    card = deck.pop()
    hand.append(card)
    show_card(card, hand == player_hand, hidden)
    return card

def calculate_score(hand):
    score = 0
    ace_count = 0
    for rank, suit in hand:
        if rank.isdigit():
            score += int(rank)
        elif rank in ("J", "Q", "K"):
            score += 10
        elif rank == "A":
            ace_count += 1
            score += 11
    while score > 21 and ace_count > 0:
        score -= 10
        ace_count -= 1
    return score


def deal_card(hand, hidden=False):
    card = deck.pop()
    hand.append(card)
    show_card(card, hand == player_hand, hidden)
    return card



def show_card(card, player, hidden=False):
    rank, suit = card
    card_image_path = f"card_images/{rank}{suit}.png"  # Формируем путь к изображению карты
    try:
        card_image = Image.open(card_image_path).resize((70, 100))
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл изображения {card_image_path} не найден.")
        return

    card_photo = ImageTk.PhotoImage(card_image)
    if player:
        card_label = tk.Label(player_frame, image=card_photo)
        card_label.image = card_photo
        card_label.pack(side=tk.LEFT)
        player_cards.append(card_label)
    else:
        card_label = tk.Label(dealer_frame)  # Создаем label без изображения
        card_label.pack(side=tk.LEFT)
        dealer_cards.append(card_label)

        if hidden:
            try:
                hidden_card_image = Image.open("card_images/back_card.png").resize((70, 100))
                hidden_card_photo = ImageTk.PhotoImage(hidden_card_image)
                card_label.config(image=hidden_card_photo)
                card_label.image = hidden_card_photo  # Скрываем карту
                card_label.hidden_card = card_photo  # Сохраняем изображение лицевой стороны
            except FileNotFoundError:
                messagebox.showerror("Ошибка", "Файл изображения card_images/back_card.png не найден.")
                return
        else:
            card_label.config(image=card_photo)
            card_label.image = card_photo

def clear_table():
    global player_cards, dealer_cards
    for card_label in player_cards + dealer_cards:
        card_label.destroy()
    player_cards = []
    dealer_cards = []
    player_score_label.config(text="")
    dealer_score_label.config(text="")
    result_label.config(text="")


def start_game():
    global player_balance, deck, player_hand, dealer_hand, player_score, dealer_score, bet_amount # Добавлено global player_balance

    try:
        bet_amount = int(bet_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректную сумму ставки.")
        return

    if bet_amount <= 0 or bet_amount > player_balance:  # Теперь player_balance доступна
        messagebox.showerror("Ошибка", "Некорректная сумма ставки.")
        return

    player_balance -= bet_amount
    balance_label.config(text=f"Баланс: ${player_balance}")

    random.shuffle(deck)
    player_hand = []
    dealer_hand = []
    clear_table()

    create_deck()  # Создаем новую колоду в начале игры
    random.shuffle(deck)

    deal_card(player_hand)
    deal_card(dealer_hand)
    deal_card(player_hand)
    deal_card(dealer_hand, hidden=True)  # Скрываем вторую карту дилера


    player_score = calculate_score(player_hand)
    player_score_label.config(text=f"Очки игрока: {player_score}")

    if player_score == 21:
        end_game()



def hit():
    global player_score
    deal_card(player_hand)
    player_score = calculate_score(player_hand)
    player_score_label.config(text=f"Очки игрока: {player_score}")
    if player_score > 21:
        end_game()


def stand():
    end_game()

def end_game():
    global dealer_score, player_balance

    # Проверяем, есть ли карты у дилера
    if dealer_cards and hasattr(dealer_cards[-1], 'hidden_card'):  # Проверка на существование скрытой карты
        dealer_cards[-1].config(image=dealer_cards[-1].hidden_card)
        dealer_cards[-1].image = dealer_cards[-1].hidden_card  # Обновляем изображение

    while calculate_score(dealer_hand) < 17:
        deal_card(dealer_hand)

    # Показываем карты дилера
    dealer_cards[-1].config(image = dealer_cards[-1].image)
    dealer_cards[-1].image = dealer_cards[-1].image # "Переворачиваем" скрытую карту

    while calculate_score(dealer_hand) < 17:
        deal_card(dealer_hand)

    dealer_score = calculate_score(dealer_hand)
    dealer_score_label.config(text=f"Очки дилера: {dealer_score}")


    if player_score > 21:
        result_label.config(text="Перебор! Вы проиграли.")
    elif dealer_score > 21:
        result_label.config(text="Дилер перебрал! Вы выиграли!")
        player_balance += 2 * bet_amount
    elif player_score > dealer_score:
        result_label.config(text="Вы выиграли!")
        player_balance += 2 * bet_amount
    elif player_score == dealer_score:
        result_label.config(text="Ничья.")
        player_balance += bet_amount # Возвращаем ставку
    else:
        result_label.config(text="Вы проиграли.")

    balance_label.config(text=f"Баланс: ${player_balance}")




root = tk.Tk()
root.title("Двадцать Одно")


# Фрейм для баланса
balance_frame = tk.Frame(root)
balance_frame.pack(pady=10)
balance_label = tk.Label(balance_frame, text=f"Баланс: ${player_balance}", font=("Arial", 16))
balance_label.pack()


# Фрейм для ставки
bet_frame = tk.Frame(root)
bet_frame.pack(pady=5)
bet_label = tk.Label(bet_frame, text="Ставка:", font=("Arial", 12))
bet_label.pack(side=tk.LEFT)
bet_entry = tk.Entry(bet_frame, font=("Arial", 12))
bet_entry.pack(side=tk.LEFT)


# Фрейм для дилера
dealer_frame = tk.Frame(root)
dealer_frame.pack(pady=10)
dealer_score_label = tk.Label(dealer_frame, text="", font=("Arial", 14))
dealer_score_label.pack()

# Фрейм для игрока
player_frame = tk.Frame(root)
player_frame.pack(pady=10)
player_score_label = tk.Label(player_frame, text="", font=("Arial", 14))
player_score_label.pack()

# Фрейм для кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Начать игру", command=start_game)
start_button.pack(side=tk.LEFT, padx=5)


hit_button = tk.Button(button_frame, text="Взять карту", command=hit)
hit_button.pack(side=tk.LEFT, padx=5)

stand_button = tk.Button(button_frame, text="Хватит", command=stand)
stand_button.pack(side=tk.LEFT, padx=5)

# Фрейм для результата
result_frame = tk.Frame(root)
result_frame.pack(pady=10)
result_label = tk.Label(result_frame, text="", font=("Arial", 16), fg="red")
result_label.pack()


root.mainloop()
