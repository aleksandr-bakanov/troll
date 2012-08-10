# coding=utf-8
# Различные игровые константы (возможно будет разделение на большее
# количество файлов)

# Игровые константы
TOTAL_ENERGY = 100
PLACE_ARMOUR = 1
PLACE_PANTS = 2
PLACE_HAND_WEAPON = 3
PLACE_BELT_WEAPON = 4

# Размеры данных
BOOL_SIZE = 1
CHAR_SIZE = 1
SHORT_SIZE = 2
INT_SIZE = 4

# Server side commands ids
S_TRACE = 1
S_LOGIN_FAILURE = 3
S_REGISTER_SUCCESS = 5
S_REGISTER_FAILURE = 7
S_LOGIN_SUCCESS = 9
S_FULL_PARAMS = 11
S_ITEM_INFO = 13
S_SHOP_ITEMS = 15
S_ADD_ITEM = 17
S_CLIENT_MONEY = 19
S_NEW_BID = 21
S_REMOVE_BID = 23
S_UPDATE_BID = 25

# Client side commands ids
C_LOGIN = 2
C_REGISTER = 4
C_ITEM_INFO = 6
C_WEAR_ITEM = 8
C_DROP_ITEM = 10
C_BUY_ITEM = 12
C_SELL_ITEM = 14
C_ADD_STAT = 16
C_ENTER_BID = 18
C_EXIT_BID = 20
C_CREATE_BID = 22
