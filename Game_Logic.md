이 코드는 reflex.dev를 사용하여 Trust Game을 두 섹션으로 나누어 구성한 실험용 웹 앱의 상태 관리 로직입니다.
각 섹션에서 사용자의 역할이 다르고, 게임 로직과 UI 전환이 이를 반영하도록 설계되어 있습니다. 아래는 전체 구조 및 작동 방식에 대한 단계별 자세한 설명입니다.

✅ 전체 흐름 요약

구분	역할	설명
Section 1	User = Player B	컴퓨터가 투자한 돈을 내가 얼마나 돌려줄지 결정
Section 2	User = Player A	각기 다른 성격 프로파일을 가진 AI 상대에게 투자하고, 그에 따라 반환 금액을 받음


🔹 Section 1: User가 Player B가 되는 상황

TrustGameState.current_page = 1
	1.	시작 전 설정 (start_section_1)
	•	INITIAL_BALANCE로 Player A의 초기 자산 설정 (10)
	•	simulate_player_a_decision() 호출 → Player A가 무작위로 투자 금액(amount_to_send) 결정
	•	received_amount는 amount_to_send * PROLIFERATION_FACTOR로 계산됨 (3배)
	2.	사용자는 이 받은 금액 중 일부 (amount_to_return)를 반환
	•	submit_player_b_decision() 호출 시:
	•	player_b_profit = received_amount - amount_to_return
	•	player_a_profit = amount_to_return - amount_to_send
	•	두 플레이어의 balance 업데이트
	•	다음 라운드로 이동 (current_round += 1)하거나 다음 섹션으로 전환 (current_page = 2)
	3.	총 NUM_ROUNDS (기본 10회) 반복


🔹 Section 2: User가 Player A가 되는 상황

TrustGameState.current_page = 3
	1.	시작 시 start_section_2() 호출:
	•	AI(Player B)들의 성격 프로파일을 무작위로 섞어 저장 (shuffled_profiles)
	•	Stage = 성격 하나 (총 N개의 프로파일 → N 스테이지)
	2.	각 스테이지에서:
	•	select_player_b_profile()로 현재 AI의 성격 프로파일 적용
	•	사용자는 투자 금액 amount_to_send를 입력
	•	main_algorithm() 호출되면 반환 금액(amount_to_return)을 다음 방식으로 계산:

💡 반환 계산 공식: calculate_player_b_return()

base_return_rate = N(loc=base_fairness + generosity_bias, scale=fairness_variance)
↓
base_return = received_amount * base_return_rate
↓
감소 요인 (large investment bias, end-game fairness drop 등) 적용
↓
최소 0, 최대 received_amount 사이로 반환 금액 결정

	3.	각 라운드에서:
	•	amount_to_send, amount_to_return, profit, personality, timestamp 등을 저장 (round_history, save_experiment_data)
	•	10라운드 후 current_stage 증가 (다음 성격 프로파일로 이동)
	•	모든 스테이지가 끝나면 current_page = 4 (End 페이지)

⸻

🧠 주요 게임 메커니즘 요약

항목	설명
PROLIFERATION_FACTOR	투자 금액이 몇 배로 증식되는지 결정 (기본값: 3)
received_amount	amount_to_send * 3
calculate_player_b_return()	AI의 성격에 따라 행동 모델링 (정규분포 기반)
round_history	각 라운드 데이터 저장 및 Firebase 업로드


⸻

🔐 인증 관련 기능
	•	login(), register(), logout() 함수는 Firebase 기반 사용자 인증을 처리
	•	인증 성공 시 사용자 user_id를 저장하고, 추후 round_history에 연결

⸻

📊 실험의 구조적 특징

특징	구현 방식
두 가지 역할	각각 Player A와 B의 입장에서 실험 수행
AI의 성격 프로파일	TOML 파일(personalities.toml)에서 로드, 정규분포 기반 모델링
단계별 기록	스테이지별 10라운드 * N스테이지 반복
데이터 저장	Firebase Firestore 연동 (via save_experiment_data)


⸻

🛠️ 디버깅/테스트 포인트
	•	print() 문: 투자 금액, 반환 금액, 성격 등 디버깅 정보 확인 가능
	•	amount_to_send과 amount_to_return은 각 섹션에서 유효성 검사 및 입력 필터링 처리
	•	reset_game_state() 호출로 전체 상태 초기화 가능

⸻

필요하다면 Section 1/2에 대한 UI 플로우 또는 personality.toml의 구조, Firebase 데이터 스키마 등도 추가로 설명해줄 수 있어!