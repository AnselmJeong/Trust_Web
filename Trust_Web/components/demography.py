import reflex as rx
from Trust_Web.demographic_state import DemographicState

# Helper function for creating diagnosis checkboxes
def create_diagnosis_checkbox(diag_item: str) -> rx.Component:
    return rx.checkbox(
        diag_item,
        name=f"diagnosis_{diag_item}"
    )

def demography_form() -> rx.Component:
    return rx.center( # Center the entire form container
        rx.form(
            rx.vstack(
                rx.heading("Demographic Information", size="3", margin_bottom="1em"),
                rx.divider(margin_bottom="1em"),                
                rx.grid(
                    # Column 1
                    rx.vstack(
                        # 성별 (Gender)
                        rx.form.field(
                            rx.form.label(rx.text("⚤ 성별")),
                            rx.radio_group.root(
                                rx.hstack(
                                    rx.radio_group.item("남성", value="male"),
                                    rx.radio_group.item("여성", value="female"),
                                    spacing="4",
                                ),
                                name="gender",
                            ),
                            name="gender_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 생년월일 (birth date - personal)
                        rx.form.field(
                            rx.form.label(rx.text("📅 생년월일")),
                            rx.hstack( 
                                rx.input(
                                    placeholder="20210430",
                                    name="birth_date",
                                    width="160px",
                                    type_="date"
                                )
                            ),
                            name="birthdate_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 학력 (Education)
                        rx.form.field(
                            rx.form.label(rx.text("🎓 학력")),
                            rx.select(
                                ["고등학교 졸업 이하", "대학교 재학/휴학/중퇴", "대학교 졸업", "대학원 재학/휴학/중퇴", "대학원 졸업"],
                                placeholder="선택하세요",
                                name="education_level",
                                width="160px",
                            ),
                            name="education_level_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 직업 (Occupation)
                        rx.form.field(
                            rx.form.label(rx.text("💼 직업")),
                            rx.select(
                                ["학생", "직장인", "자영업자", "전문직", "주부", "무직", "기타"],
                                placeholder="선택하세요",
                                name="occupation",
                            ),
                            name="occupation_field",
                            style={"margin_bottom": "1em"},
                        ),
                        spacing="4", # Spacing for vstack in column 1
                        align_items="start",
                        width="100%", # Ensure vstack takes full width of its grid cell
                    ),
                    # Column 2
                    rx.vstack(
                        # 정신과 병력 (Psychiatric History)
                        rx.form.field(
                            rx.form.label(rx.text("🧠 정신과 병력")),
                            rx.radio_group.root(
                                rx.hstack(
                                    rx.radio_group.item("없음", value="no"),
                                    rx.radio_group.item("있음", value="yes"),
                                    spacing="4",
                                ),
                                name="has_psychiatric_history",
                            ),
                            name="has_psychiatric_history_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 과거 진단명 (Past Diagnoses)
                        rx.form.field(
                            rx.form.label(rx.text("🩺 과거 진단명")),
                            rx.vstack( 
                                rx.grid(
                                    rx.foreach( 
                                        DemographicState.diagnosis_options, 
                                        create_diagnosis_checkbox
                                    ),
                                    columns="2",
                                    spacing="2",
                                    width="100%"
                                ),
                                align_items="start"
                            ),
                            name="past_diagnoses_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 발병시기 (Onset of illness - diagnosis related)
                        rx.form.field(
                            rx.form.label(rx.text("📅 발병시기 (진단 관련)")),
                            rx.input(
                                placeholder="예: 우울증 3년전, 공황장애 1년 6개월전",
                                name="onset_of_diagnosis_details",
                                width="240px",
                            ),
                            name="onset_of_diagnosis_details_field",
                            style={"margin_bottom": "1em"},
                        ),
                        # 정신과 약물 복용중 (Moved here)
                        rx.form.field(
                            rx.form.label(rx.text("💊 정신과 약물 복용중")),
                            rx.radio_group.root(
                                rx.hstack(
                                    rx.radio_group.item("네", value="yes"),
                                    rx.radio_group.item("아니오", value="no"),
                                    spacing="4",
                                ),
                                name="on_psychiatric_medication",
                            ),
                            name="on_psychiatric_medication_field",
                            style={"margin_bottom": "1em", "margin_top": "1em"}, # Add margin_top for spacing
                        ),
                        # 심리상담중 (Moved here)
                        rx.form.field(
                            rx.form.label(rx.text("💬 심리상담중")),
                            rx.radio_group.root(
                                rx.hstack(
                                    rx.radio_group.item("네", value="yes"),
                                    rx.radio_group.item("아니오", value="no"),
                                    spacing="4",
                                ),
                                name="in_psychological_counseling",
                            ),
                            name="in_psychological_counseling_field",
                            style={"margin_bottom": "1em"},
                        ),
                        spacing="4", # Spacing for vstack in column 2
                        align_items="start",
                        width="100%", # Ensure vstack takes full width of its grid cell
                    ),
                    columns="2", # Two columns for the main grid
                    spacing="6", # Spacing between the two columns
                ),
                
                # Removed the separate grid for medication/counseling sections

                rx.center( 
                    rx.form.submit(
                        rx.button("제출", margin_top="2em", type_="submit", width="160px")
                    ),
                    width="100%"
                ),
                spacing="4", # Overall vstack spacing
                align_items="stretch", # Stretch items to fill width if needed
                padding="2em", # Reduced padding a bit
                max_width="1000px", # Max width for the vstack containing the form elements
                width="100%",      # Ensure it takes up available space up to max_width
                margin_x="auto",  # Added this to center the vstack itself
            ),
            on_submit=DemographicState.handle_submit,
            reset_on_submit=True,
            # max_width and width for form itself might be redundant if parent vstack controls it
            # but doesn't hurt to ensure it. Let's try with vstack controlling it first.
        ),
        width="100%", # rx.center takes full width to center its child
        height="100%", # Make center take full height to better center vertically if needed
        # style={"border": "1px solid red"} # Debugging: to see the bounds of rx.center
    )