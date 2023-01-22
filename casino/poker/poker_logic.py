import collections

def determine_winner(players, dealer_hand):
    player_card_map = collections.defaultdict(list)
    for player in players:
        hand = convert_cards(player.hand, dealer_hand)
        hand_value, highest_card = determine_hand_value(hand)
        player_card_map[(hand_value, highest_card)].append(player)
    
    winning_card_value = max(player_card_map.keys(), key=lambda x : (x[0], x[1]))

    return player_card_map[winning_card_value]

def convert_cards(cards, dealer_hand):
    converted_cards = []
    suits = {"Diamonds": "D", "Clubs": "C", "Hearts": "H", "Spades": "S"}
    cards += dealer_hand
    for card in cards:
        value = card.value
        if value == 1:
            value = 14 #Ace is the largest
        suit = suits[card.suit_name]
        curr_card = str(value) + suit
        converted_cards.append(curr_card)
    converted_cards.sort(key=lambda x : int(x[0]))
    return converted_cards

def determine_hand_value(cards):
    check_straight_flush_card = check_straight_flush(cards)
    if check_straight_flush_card:
        return (9, check_straight_flush_card)
    check_four_of_a_kind_card = check_four_of_a_kind(cards)
    if check_four_of_a_kind_card:
        return (8, check_four_of_a_kind_card)
    check_full_house_card = check_full_house(cards)
    if check_full_house_card:
        return (7, check_full_house_card)
    check_flush_card = check_flush(cards)
    if check_flush_card:
        return (6, check_flush_card)
    check_straight_card = check_straight(cards)
    if check_straight_card:
        return (5, check_straight_card)
    check_three_of_a_kind_card = check_three_of_a_kind(cards)
    if check_three_of_a_kind_card:
        return (4, check_three_of_a_kind_card)
    check_two_pair_card = check_two_pair(cards)
    if check_two_pair_card:
        return (3, check_two_pair_card)
    check_pair_card = check_pair(cards)
    if check_pair_card:
        return (2, check_pair_card)
    return (1, int(cards[-1][0]))

def check_straight_flush(cards):
    if check_flush(cards) and check_straight(cards):
        return check_straight(cards)
    return False

def check_four_of_a_kind(cards):
    same_number_count = collections.defaultdict(int)
    for card in cards:
        num = card[0]
        same_number_count[num] += 1
        if same_number_count[num] == 4:
            return int(num)
    return False

def check_full_house(cards):
    same_number_count = collections.defaultdict(int)
    for card in cards:
        num = card[0]
        same_number_count[num] += 1
    cards_count = [(card, value) for card, value in same_number_count.items()] 
    cards_count.sort(key=lambda x: int(x[1]))
    if cards_count[-1][1] == str(3) and cards_count[-2][1] == str(3):
        if int(cards_count[-1][0]) > int(cards_count[-2][0]):
            return int(cards_count[-1][0])
        return int(cards_count[-2][0])
    elif cards_count[-1][1] == str(2) and cards_count[-2][1] == str(3):
        return cards_count[-2][0]
    elif cards_count[-1][1] == str(3) and cards_count[-2][1] == str(2):
        return cards_count[-1][0]
    return False

def check_flush(cards):
    same_suit_count = collections.defaultdict(int)
    largest_card = 0
    for card in cards:
        suit = card[1]
        same_suit_count[suit] += 1
        if same_suit_count[suit] >= 5:
            largest_card = max(largest_card, int(card[0]))
    if largest_card == 0:
        return False
    return largest_card

def check_straight(cards):
    sorted_cards = cards[::-1]
    counter = 1
    prev = int(sorted_cards[0][0])
    starting_card = prev

    for card in sorted_cards[1:]:
        curr_num = int(card[0])
        if prev - 1 == curr_num:
            counter += 1
            if counter == 5:
                return starting_card
        else:
            counter = 1
            starting_card = curr_num
        prev = curr_num

    return False

def check_three_of_a_kind(cards):
    same_number_count = collections.defaultdict(int)
    for card in cards:
        num = card[0]
        same_number_count[num] += 1
        if same_number_count[num] == 3:
            return int(num)
    return False

def check_two_pair(cards):
    same_number_count = collections.defaultdict(int)
    pairs = 0
    max_pair_num = 0
    for card in cards:
        num = card[0]
        same_number_count[num] += 1
        if same_number_count[num] == 2:
            pairs += 1
            if pairs == 2:
                max_pair_num = max(max_pair_num, int(num))
    if max_pair_num == 0:
        return False
    return max_pair_num

def check_pair(cards):
    same_number_count = collections.defaultdict(int)
    for card in cards:
        num = card[0]
        same_number_count[num] += 1
        if same_number_count[num] == 2:
            return int(num)
    return False