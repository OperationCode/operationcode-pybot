from modules.airtable.daily_programmer_table import DailyProgrammerTable
from modules.airtable.mentorship_tables import (
    MentorshipServicesTable,
    MentorshipSkillsetsTable,
    MentorshipRequestsTable,
    MentorshipMentorsTable,
    MentorshipAffiliationsTable,
)
from modules.airtable.message_text_table import MessageTextTable
from modules.airtable.scheduled_message_table import ScheduledMessagesTable

# General message related tables
message_text_table = MessageTextTable()

# Scheduled message related tables
scheduled_message_table = ScheduledMessagesTable()

# Daily Programmer related table
daily_programmer_table = DailyProgrammerTable()

# Mentorship related tables
mentor_table = MentorshipMentorsTable()
mentorship_services_table = MentorshipServicesTable()
mentorship_skillsets_table = MentorshipSkillsetsTable()
mentorship_requests_table = MentorshipRequestsTable()
mentorship_affiliations_table = MentorshipAffiliationsTable()
