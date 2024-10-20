import streamlit as st
import datetime
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

# Data Models
@dataclass
class User:
    id: str
    name: str
    age: int
    gender: str
    online: bool = True
    last_active: datetime.datetime = datetime.datetime.now()

@dataclass
class Message:
    id: str
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime.datetime
    is_read: bool = False

@dataclass
class Group:
    id: str
    name: str
    creator_id: str
    members: List[str]
    created_at: datetime.datetime

def init_session_state():
    """Initialize session state variables"""
    if 'users' not in st.session_state:
        st.session_state.users = {}  # Dict[str, User]
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # List[Message]
    if 'groups' not in st.session_state:
        st.session_state.groups = {}  # Dict[str, Group]
    if 'active_chats' not in st.session_state:
        st.session_state.active_chats = set()  # Set of open chat windows
    if 'unread_counts' not in st.session_state:
        st.session_state.unread_counts = {}  # Dict[str, int]
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "login"

def get_unread_messages_count(user_id: str) -> int:
    """Get count of unread messages for a user"""
    return sum(1 for msg in st.session_state.messages 
              if msg.receiver_id == user_id and not msg.is_read)

def login_page():
    """Render the login page"""
    st.title("💬 Professional Chat Platform")
    
    with st.form("login_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=100, value=25)
        with col2:
            gender = st.selectbox("Gender", ["Select Gender", "Male", "Female", "Other"])
        
        submit = st.form_submit_button("Join Platform", use_container_width=True)
        
        if submit and name and gender != "Select Gender":
            user_id = str(uuid.uuid4())
            new_user = User(
                id=user_id,
                name=name,
                age=age,
                gender=gender
            )
            st.session_state.users[user_id] = new_user
            st.session_state.current_user = new_user
            st.session_state.current_page = "main"
            st.rerun()

def render_chat_window(other_user_id: str):
    """Render a chat window for a specific user"""
    other_user = st.session_state.users[other_user_id]
    
    # Get chat history
    chat_messages = [
        msg for msg in st.session_state.messages 
        if (msg.sender_id in [st.session_state.current_user.id, other_user_id] and 
            msg.receiver_id in [st.session_state.current_user.id, other_user_id])
    ]
    
    # Chat container
    chat_container = st.container()
    
    # Message input
    with st.form(key=f"chat_form_{other_user_id}", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            message = st.text_input("Type your message...", key=f"message_input_{other_user_id}")
        with col2:
            submit = st.form_submit_button("Send")
        
        if submit and message:
            new_message = Message(
                id=str(uuid.uuid4()),
                sender_id=st.session_state.current_user.id,
                receiver_id=other_user_id,
                content=message,
                timestamp=datetime.datetime.now()
            )
            st.session_state.messages.append(new_message)
            st.rerun()
    
    # Display messages
    with chat_container:
        for msg in sorted(chat_messages, key=lambda x: x.timestamp):
            is_current_user = msg.sender_id == st.session_state.current_user.id
            sender = st.session_state.users[msg.sender_id]
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{sender.name}**")
            with col2:
                st.write(msg.content)
            st.write(f"*{msg.timestamp.strftime('%H:%M:%S')}*")
            st.markdown("---")

def render_group_chat(group_id: str):
    """Render a group chat window"""
    group = st.session_state.groups[group_id]
    
    # Get group messages
    group_messages = [
        msg for msg in st.session_state.messages 
        if msg.receiver_id == group_id
    ]
    
    st.subheader(f"📱 {group.name}")
    
    # Members list
    with st.expander("Group Members"):
        for member_id in group.members:
            member = st.session_state.users[member_id]
            st.write(f"{'🟢' if member.online else '⚫'} {member.name}")
    
    # Chat container
    chat_container = st.container()
    
    # Message input
    with st.form(key=f"group_chat_form_{group_id}", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            message = st.text_input("Type your message...", key=f"group_message_input_{group_id}")
        with col2:
            submit = st.form_submit_button("Send")
        
        if submit and message:
            new_message = Message(
                id=str(uuid.uuid4()),
                sender_id=st.session_state.current_user.id,
                receiver_id=group_id,
                content=message,
                timestamp=datetime.datetime.now()
            )
            st.session_state.messages.append(new_message)
            st.rerun()
    
    # Display messages
    with chat_container:
        for msg in sorted(group_messages, key=lambda x: x.timestamp):
            sender = st.session_state.users[msg.sender_id]
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{sender.name}**")
            with col2:
                st.write(msg.content)
            st.write(f"*{msg.timestamp.strftime('%H:%M:%S')}*")
            st.markdown("---")

def main_page():
    """Render the main chat interface"""
    # Sidebar with online users and groups
    with st.sidebar:
        st.title("👥 Online Users")
        for user_id, user in st.session_state.users.items():
            if user_id != st.session_state.current_user.id:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{'🟢' if user.online else '⚫'} {user.name}")
                with col2:
                    if st.button("Chat", key=f"chat_btn_{user_id}"):
                        st.session_state.active_chats.add(user_id)
        
        st.markdown("---")
        
        # Create new group
        st.subheader("👥 Create New Group")
        with st.form("create_group_form"):
            group_name = st.text_input("Group Name")
            available_users = [user for user_id, user in st.session_state.users.items() 
                             if user_id != st.session_state.current_user.id]
            selected_users = st.multiselect(
                "Add Members",
                options=[user.name for user in available_users],
                format_func=lambda x: x
            )
            
            if st.form_submit_button("Create Group"):
                if group_name and selected_users:
                    group_id = str(uuid.uuid4())
                    member_ids = [st.session_state.current_user.id]
                    for user in available_users:
                        if user.name in selected_users:
                            member_ids.append(user.id)
                    
                    new_group = Group(
                        id=group_id,
                        name=group_name,
                        creator_id=st.session_state.current_user.id,
                        members=member_ids,
                        created_at=datetime.datetime.now()
                    )
                    st.session_state.groups[group_id] = new_group
                    st.rerun()
        
        # Display existing groups
        if st.session_state.groups:
            st.markdown("---")
            st.subheader("👥 Your Groups")
            for group_id, group in st.session_state.groups.items():
                if st.session_state.current_user.id in group.members:
                    if st.button(f"📱 {group.name}", key=f"group_btn_{group_id}"):
                        st.session_state.active_chats.add(f"group_{group_id}")
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Welcome, {st.session_state.current_user.name}!")
        
        # Display unread message count
        unread_count = get_unread_messages_count(st.session_state.current_user.id)
        if unread_count > 0:
            st.info(f"You have {unread_count} unread messages")
    
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.current_user = None
            st.session_state.current_page = "login"
            st.rerun()
    
    # Active chat windows
    for chat_id in list(st.session_state.active_chats):
        with st.expander(f"Chat with {st.session_state.users[chat_id].name if not chat_id.startswith('group_') else st.session_state.groups[chat_id[6:]].name}", expanded=True):
            if chat_id.startswith('group_'):
                render_group_chat(chat_id[6:])
            else:
                render_chat_window(chat_id)
            
            if st.button("Close Chat", key=f"close_{chat_id}"):
                st.session_state.active_chats.remove(chat_id)
                st.rerun()

def main():
    init_session_state()
    
    if st.session_state.current_page == "login":
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Professional Chat Platform",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
