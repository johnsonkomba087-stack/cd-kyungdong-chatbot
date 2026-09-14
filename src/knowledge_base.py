"""
Sample knowledge base for Kyungdong University Global Campus
"""

from typing import List

UNIVERSITY_DOCUMENTS = [
    {
        "id": "admission_001",
        "content": "Kyungdong University Global Campus offers diverse undergraduate programs in Engineering, Business, Arts & Sciences, and Health Sciences. International students can apply through our online portal. Application requirements include: completed application form, official transcripts, English proficiency test (TOEFL/IELTS), and statement of purpose.",
        "source": "Admissions Office",
        "category": "admissions"
    },
    {
        "id": "admission_002",
        "content": "Application deadlines vary by program. Spring semester applications are due by November 30, and fall semester applications by May 31. Early application is recommended as some programs have rolling admissions.",
        "source": "Admissions Office",
        "category": "admissions"
    },
    {
        "id": "programs_001",
        "content": "Our Engineering programs include Computer Science, Mechanical Engineering, Chemical Engineering, and Civil Engineering. All programs are accredited and offer both theory and practical lab experience.",
        "source": "College of Engineering",
        "category": "programs"
    },
    {
        "id": "programs_002",
        "content": "Business programs include Bachelor of Business Administration (BBA), accounting, finance, marketing, and international business. Students can participate in internship programs with leading corporations.",
        "source": "College of Business",
        "category": "programs"
    },
    {
        "id": "scholarship_001",
        "content": "Merit-based scholarships are available for high-achieving students. Presidential Scholarships cover 50-100% of tuition. Academic Excellence Scholarships cover 30-50%. All incoming students are automatically considered for merit scholarships.",
        "source": "Financial Aid Office",
        "category": "scholarships"
    },
    {
        "id": "scholarship_002",
        "content": "Need-based financial aid is available to demonstrated need students. International students can apply for tuition assistance, living expense support, and work-study opportunities on campus.",
        "source": "Financial Aid Office",
        "category": "scholarships"
    },
    {
        "id": "fees_001",
        "content": "Undergraduate tuition for 2024-2025 academic year: International students pay approximately $30,000-35,000 USD per year depending on the program. Engineering programs may have slightly higher rates.",
        "source": "Office of the Registrar",
        "category": "fees"
    },
    {
        "id": "fees_002",
        "content": "Additional costs include: dormitory fees ($4,000-6,000/year), meal plan ($3,000-4,000/year), books and supplies ($1,500/year), personal expenses ($2,000/year). Total estimated cost ranges from $40,000-50,000 USD annually.",
        "source": "Office of the Registrar",
        "category": "fees"
    },
    {
        "id": "campus_001",
        "content": "The Global Campus features state-of-the-art facilities including computer labs, science centers, sports complex with gymnasium and swimming pool, library with 500,000+ volumes, and modern student lounges.",
        "source": "Campus Life Office",
        "category": "campus_life"
    },
    {
        "id": "campus_002",
        "content": "Student housing is provided for all international students in modern dormitories with amenities including 24-hour internet, laundry facilities, common kitchens, and organized social events.",
        "source": "Housing Office",
        "category": "campus_life"
    },
    {
        "id": "services_001",
        "content": "International Student Services provides visa support, orientation programs, cultural integration activities, language support, and emergency assistance. Dedicated advisors help with adjustment to campus life.",
        "source": "International Student Services",
        "category": "student_services"
    },
    {
        "id": "services_002",
        "content": "Academic support services include tutoring centers, writing labs, study groups, career counseling, and mental health services. All services are free for enrolled students.",
        "source": "Student Support Services",
        "category": "student_services"
    },
]


def load_knowledge_base() -> List[dict]:
    """Load university knowledge base"""
    return UNIVERSITY_DOCUMENTS