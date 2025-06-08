import pygame
import os
import random

# ───────────────────────────── 초기 설정 ─────────────────────────────
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("One Card")

WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)

# 폰트 (Nanum Gothic - 없으면 기본 폰트 사용)
try:
  FONT_PATH = os.path.join(os.getcwd(), "Nanum_Gothic", "NanumGothic-Bold.ttf")
  pygame.font.Font(FONT_PATH, 24)
except FileNotFoundError:
  FONT_PATH = None
FONT = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else pygame.font.SysFont(None, 24)

CARD_WIDTH, CARD_HEIGHT = 100, 145
CARD_FOLDER = 'cards'  # 카드 이미지 폴더

# ───────────────────────────── 자원 불러오기 ─────────────────────────────
def load_card_images():
  card_images = {}
  suits = ['hearts', 'diamonds', 'clubs', 'spades']
  values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
  for suit in suits:
    for value in values:
      filename = f"{value}_of_{suit}.png"
      path = os.path.join(CARD_FOLDER, filename)
      image = pygame.image.load(path).convert_alpha()
      image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
      card_images[(value, suit)] = image
  return card_images

CARD_IMAGES = load_card_images()

# ───────────────────────────── 카드 / 덱 헬퍼 ─────────────────────────────
def create_deck():
  suits = ['hearts', 'diamonds', 'clubs', 'spades']
  values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
  deck = [(value, suit) for suit in suits for value in values]
  random.shuffle(deck)
  return deck

def refill_deck_from_discard(deck, discard_pile):
  if len(discard_pile) > 1:
    top_card = discard_pile[-1]
    rest = discard_pile[:-1]
    random.shuffle(rest)
    deck.extend(rest)
    discard_pile[:] = [top_card]

def draw_card_from_deck(deck, discard_pile, hand):
  if len(deck) == 0:
    refill_deck_from_discard(deck, discard_pile)
  if len(deck) > 0:
    hand.append(deck.pop())

# ───────────────────────────── 그리기 헬퍼 ─────────────────────────────
def draw_card_with_white_bg(card_image, pos):
  rect = card_image.get_rect(topleft=pos)
  pygame.draw.rect(WIN, WHITE, rect)
  pygame.draw.rect(WIN, BLACK, rect, 2)
  WIN.blit(card_image, pos)

def draw_hand(hand, x, y, max_width=700, selected_index=None):
  num_cards = len(hand)
  if num_cards == 0:
    return
  spacing = min((max_width - CARD_WIDTH) / (num_cards - 1), CARD_WIDTH + 10) if num_cards > 1 else 0
  for i, card in enumerate(hand):
    pos_x = x + i * spacing
    pos_y = y
    if selected_index is not None and i == selected_index:
      scaled = pygame.transform.scale(CARD_IMAGES[card], (int(CARD_WIDTH * 1.2), int(CARD_HEIGHT * 1.2)))
      scaled_pos = (pos_x - (scaled.get_width() - CARD_WIDTH) // 2, pos_y - 20)
      rect = scaled.get_rect(topleft=scaled_pos)
      pygame.draw.rect(WIN, WHITE, rect)
      pygame.draw.rect(WIN, BLACK, rect, 2)
      WIN.blit(scaled, scaled_pos)
    else:
      draw_card_with_white_bg(CARD_IMAGES[card], (pos_x, pos_y))

def draw_text(text, x, y, size=24, color=WHITE):
  font = pygame.font.Font(FONT_PATH, size) if FONT_PATH else pygame.font.SysFont(None, size)
  label = font.render(text, True, color)
  WIN.blit(label, (x, y))

def draw_centered_text(text, y, size=32, color=WHITE):
  font = pygame.font.Font(FONT_PATH, size) if FONT_PATH else pygame.font.SysFont(None, size)
  surface = font.render(text, True, color)
  rect = surface.get_rect(center=(WIDTH // 2, y))
  WIN.blit(surface, rect)

# ───────────────────────────── 게임 규칙 헬퍼 ─────────────────────────────
def can_play(card, top_card, draw_stack):
  if draw_stack > 0:
    return card[0] in ['2', 'ace']  # 스택 중엔 공격 카드만
  return card[0] == top_card[0] or card[1] == top_card[1]

def apply_card_effect(card, state):
  """카드를 낸 직후 스택·스킵·추가턴 등을 업데이트"""
  value = card[0]
  if value == '2':
    state['draw_stack'] += 2
    state['skip_turn'] = False
    state['extra_turn'] = False
  elif value == 'ace':
    state['draw_stack'] += 3
    state['skip_turn'] = False
    state['extra_turn'] = False
  elif value == 'jack':
    state['skip_turn'] = True
    state['extra_turn'] = False
  elif value == 'king':
    state['extra_turn'] = True  # 한 번만
  else:
    state['skip_turn'] = False
    state['extra_turn'] = False

# ───────────────────────────── 메인 루프 ─────────────────────────────
def main():
  deck = create_deck()
  player_hand = [deck.pop() for _ in range(7)]
  computer_hand = [deck.pop() for _ in range(7)]
  discard_pile = [deck.pop()]

  state = {
    'draw_stack': 0,
    'skip_turn': False,
    'extra_turn': False,
  }

  running = True
  player_turn = True
  selected_index = 0
  game_over = False
  status_msg = "←/→ 선택, Enter 내기, Space 뽑기"

  clock = pygame.time.Clock()

  while running:
    # ───────────────── 표면 그리기 ─────────────────
    WIN.fill(GREEN)

    draw_text("버려진 카드", 50, 50)
    draw_card_with_white_bg(CARD_IMAGES[discard_pile[-1]], (50, 80))

    # 컴퓨터 카드 (뒷면)
    comp_x, comp_y = 600, 50
    for i in range(len(computer_hand)):
      rect = pygame.Rect(comp_x + i * 30, comp_y, CARD_WIDTH, CARD_HEIGHT)
      pygame.draw.rect(WIN, WHITE, rect)
      pygame.draw.rect(WIN, BLACK, rect, 3)
    draw_text(f"컴퓨터 카드 수: {len(computer_hand)}", comp_x, comp_y + CARD_HEIGHT + 10)

    # 중앙 알림
    if game_over:
      result = "당신이 이겼습니다!" if len(player_hand) == 0 else "컴퓨터가 이겼습니다."
      draw_centered_text(result, HEIGHT // 2, size=40)
    else:
      turn_str = "당신의 차례" if player_turn else "컴퓨터 차례"
      draw_centered_text(turn_str, 260)

    # 스택·스킵 메시지
    effect_msgs = []
    if state['draw_stack'] > 0:
      effect_msgs.append(f"※ 다음 플레이어가 카드 {state['draw_stack']}장 뽑아야 합니다!")
    if state['skip_turn']:
      effect_msgs.append("※ 다음 플레이어 턴이 건너뜁니다!")
    if effect_msgs:
      draw_centered_text(" / ".join(effect_msgs), 295, size=20)

    # 플레이어 핸드
    draw_text("당신의 카드", 50, 300)
    draw_hand(player_hand, 50, 330, max_width=700, selected_index=selected_index)

    # 상태바
    draw_centered_text(status_msg, 585, size=22)

    pygame.display.update()
    clock.tick(30)

    # ───────────────── 플레이어 스킵 처리 ─────────────────
    if player_turn and state['skip_turn'] and not game_over:
      state['skip_turn'] = False
      status_msg = "당신 턴이 건너뜁니다!"
      player_turn = False
      continue

    # ───────────────── 이벤트 처리 ─────────────────
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if game_over or not player_turn:
        continue

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
          selected_index = (selected_index + 1) % len(player_hand)
        elif event.key == pygame.K_LEFT:
          selected_index = (selected_index - 1) % len(player_hand)
        elif event.key == pygame.K_RETURN:
          if not player_hand:
            continue
          selected_card = player_hand[selected_index]

          # 스택 상황
          if state['draw_stack'] > 0 and selected_card[0] not in ['2', 'ace']:
            status_msg = "스택 중엔 2나 A만 낼 수 있어요!"
            continue

          # 일반 상황
          if state['draw_stack'] == 0 and not can_play(selected_card, discard_pile[-1], 0):
            status_msg = "낼 수 없는 카드입니다."
            continue

          # 카드 내기
          discard_pile.append(selected_card)
          player_hand.pop(selected_index)
          apply_card_effect(selected_card, state)
          status_msg = f"{selected_card[0].upper()}를 냈습니다."

          if len(player_hand) == 0:
            game_over = True

          # 추가 턴 처리
          if state['extra_turn']:
            state['extra_turn'] = False  # 한 번만 허용
          else:
            player_turn = False
            selected_index = max(0, len(player_hand) - 1)

        elif event.key == pygame.K_SPACE:
          # 카드 뽑기
          if state['draw_stack'] > 0:
            for _ in range(state['draw_stack']):
              draw_card_from_deck(deck, discard_pile, player_hand)
            status_msg = f"카드 {state['draw_stack']}장 뽑았습니다."
            state['draw_stack'] = 0
          else:
            draw_card_from_deck(deck, discard_pile, player_hand)
            status_msg = "카드를 한 장 뽑았습니다."
          player_turn = False
          selected_index = len(player_hand) - 1

    # ───────────────── 컴퓨터 턴 ─────────────────
    if not player_turn and not game_over:
      pygame.time.delay(800)
      hand = computer_hand
      top = discard_pile[-1]

      # 컴퓨터 스킵
      if state['skip_turn']:
        state['skip_turn'] = False
        status_msg = "컴퓨터 턴이 건너뜁니다!"
        player_turn = True
        continue

      # 스택 상황
      if state['draw_stack'] > 0:
        stack_cards = [c for c in hand if c[0] in ['2', 'ace']]
        if stack_cards:
          card = random.choice(stack_cards)
          discard_pile.append(card)
          hand.remove(card)
          apply_card_effect(card, state)
          status_msg = f"컴퓨터가 {card[0].upper()}를 냈습니다."
          if state['extra_turn']:
            state['extra_turn'] = False
          else:
            player_turn = False
        else:
          for _ in range(state['draw_stack']):
            draw_card_from_deck(deck, discard_pile, hand)
          status_msg = f"컴퓨터가 카드 {state['draw_stack']}장 뽑았습니다."
          state['draw_stack'] = 0
          player_turn = True

      # 일반 상황
      else:
        playable = [c for c in hand if can_play(c, top, 0)]
        if playable:
          kings = [c for c in playable if c[0] == 'king']
          card = kings[0] if kings else random.choice(playable)
          discard_pile.append(card)
          hand.remove(card)
          apply_card_effect(card, state)
          status_msg = f"컴퓨터가 {card[0].upper()}를 냈습니다."
          if len(hand) == 0:
            game_over = True
          if state['extra_turn']:
            state['extra_turn'] = False
            player_turn = False
          else:
            player_turn = True
        else:
          draw_card_from_deck(deck, discard_pile, hand)
          status_msg = "컴퓨터가 카드를 한 장 뽑았습니다."
          player_turn = True

  pygame.quit()

# ───────────────────────────── 실행 ─────────────────────────────
if __name__ == "__main__":
  main()