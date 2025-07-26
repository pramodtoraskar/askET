#!/usr/bin/env python3
"""
CLI Interface for Ask ET chatbot
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box

from src.rag_chain import create_rag_chain
from src.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class AskETCLI:
    """CLI interface for Ask ET chatbot"""
    
    def __init__(self):
        self.console = Console()
        self.rag_chain = None
        self.session_active = True
        
        # Welcome message
        self.welcome_message = """
# 🤖 Ask ET - Red Hat Emerging Technologies Assistant

Welcome to Ask ET! I'm your AI assistant specialized in Red Hat Emerging Technologies content.

I can help you learn about:
- **Red Hat blog posts** and technical articles
- **Open source projects** and GitHub repositories  
- **AI/ML technologies** and OpenShift AI
- **Edge computing** and hybrid cloud solutions
- **Developer productivity** tools and practices

## 🎯 Example Questions:
- "What does Red Hat say about OpenShift AI?"
- "Show me projects related to machine learning"
- "Summarize blogs about edge computing"
- "What are the latest Red Hat AI initiatives?"

Type `help` for commands, `quit` to exit.
"""
    
    def initialize(self):
        """Initialize the RAG chain"""
        try:
            self.console.print("🔄 Initializing Ask ET...", style="blue")
            self.rag_chain = create_rag_chain()
            self.console.print("✅ Ready to chat!", style="green")
            return True
        except Exception as e:
            self.console.print(f"❌ Error initializing: {e}", style="red")
            logger.error(f"Error initializing RAG chain: {e}")
            return False
    
    def display_welcome(self):
        """Display welcome message"""
        self.console.print(Markdown(self.welcome_message))
        self.console.print("\n" + "="*80 + "\n")
    
    def display_help(self):
        """Display help information"""
        help_text = """
## 📋 Available Commands:

- `help` - Show this help message
- `clear` - Clear conversation history
- `history` - Show conversation history
- `quit` / `exit` - Exit the chatbot
- `about` - Show information about Ask ET

## 💡 Tips:
- Ask specific questions for better answers
- Use keywords like "OpenShift", "AI", "Kubernetes", "edge computing"
- Ask for summaries, comparisons, or specific technologies
- Request source links for more information
"""
        self.console.print(Markdown(help_text))
    
    def display_about(self):
        """Display information about Ask ET"""
        about_text = """
## 🤖 About Ask ET

**Ask ET** is an AI-powered learning assistant for Red Hat Emerging Technologies content.

### 📊 Knowledge Base:
- **114+ Blog Posts** from Red Hat Emerging Technologies
- **33+ Open Source Projects** with GitHub repositories
- **Categories**: AI/ML, Edge Computing, Developer Productivity, Hybrid Cloud, Sustainability, Trust

### 🛠️ Technology Stack:
- **AI Model**: Google Gemini 1.5 Flash
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Framework**: LangChain RAG (Retrieval-Augmented Generation)
- **Embeddings**: Google Gemini Embeddings

### 🎯 Capabilities:
- Semantic search across Red Hat content
- Conversational AI with context awareness
- Source attribution and reference links
- Real-time information retrieval

Built with ❤️ for the Red Hat community.
"""
        self.console.print(Markdown(about_text))
    
    def display_history(self):
        """Display conversation history"""
        if not self.rag_chain:
            self.console.print("❌ RAG chain not initialized", style="red")
            return
        
        history = self.rag_chain.get_chat_history()
        if not history:
            self.console.print("📝 No conversation history yet.", style="yellow")
            return
        
        self.console.print("\n📚 **Conversation History:**\n", style="bold blue")
        for i, message in enumerate(history, 1):
            if hasattr(message, 'type'):
                if message.type == 'human':
                    self.console.print(f"👤 **You:** {message.content}", style="green")
                elif message.type == 'ai':
                    self.console.print(f"🤖 **Ask ET:** {message.content[:100]}...", style="blue")
            else:
                self.console.print(f"💬 **Message {i}:** {str(message)[:100]}...", style="gray")
    
    def clear_history(self):
        """Clear conversation history"""
        if self.rag_chain:
            self.rag_chain.clear_memory()
            self.console.print("🧹 Conversation history cleared!", style="green")
        else:
            self.console.print("❌ RAG chain not initialized", style="red")
    
    def format_response(self, result: dict) -> str:
        """Format the response for display"""
        answer = result.get('answer', 'No answer provided.')
        sources = result.get('sources', '')
        
        # Create formatted response
        response_parts = []
        
        # Add answer
        response_parts.append(f"## 🤖 Answer\n\n{answer}")
        
        # Add sources if available
        if sources:
            response_parts.append(f"\n## 📚 Sources\n\n{sources}")
        
        return "\n".join(response_parts)
    
    def display_response(self, result: dict):
        """Display the response with rich formatting"""
        try:
            # Format the response
            formatted_response = self.format_response(result)
            
            # Display with markdown
            self.console.print(Markdown(formatted_response))
            
            # Show additional info in a panel
            if 'relevant_docs' in result and result['relevant_docs']:
                docs = result['relevant_docs']
                table = Table(title="📊 Retrieved Documents", box=box.ROUNDED)
                table.add_column("Type", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Similarity", style="yellow")
                
                for doc in docs[:3]:  # Show top 3
                    doc_type = doc.get('type', 'Unknown')
                    title = doc.get('title', 'Unknown Title')[:50] + "..."
                    similarity = f"{doc.get('similarity_score', 0):.3f}"
                    table.add_row(doc_type, title, similarity)
                
                self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ Error displaying response: {e}", style="red")
            logger.error(f"Error displaying response: {e}")
    
    def process_query(self, query: str) -> Optional[dict]:
        """Process a user query"""
        if not self.rag_chain:
            self.console.print("❌ RAG chain not initialized", style="red")
            return None
        
        try:
            with self.console.status("[bold blue]Thinking...", spinner="dots"):
                result = self.rag_chain.query(query)
            return result
        except Exception as e:
            self.console.print(f"❌ Error processing query: {e}", style="red")
            logger.error(f"Error processing query: {e}")
            return None
    
    def run_interactive(self):
        """Run the interactive chat loop"""
        self.console.print("\n💬 **Chat Session Started**\n", style="bold green")
        
        while self.session_active:
            try:
                # Get user input
                query = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                # Handle commands
                if query.lower() in ['quit', 'exit', 'q']:
                    if Confirm.ask("Are you sure you want to exit?"):
                        self.console.print("👋 Goodbye! Thanks for using Ask ET!", style="green")
                        break
                    continue
                
                elif query.lower() == 'help':
                    self.display_help()
                    continue
                
                elif query.lower() == 'clear':
                    self.clear_history()
                    continue
                
                elif query.lower() == 'history':
                    self.display_history()
                    continue
                
                elif query.lower() == 'about':
                    self.display_about()
                    continue
                
                # Skip empty queries
                if not query.strip():
                    continue
                
                # Process the query
                result = self.process_query(query)
                if result:
                    self.display_response(result)
                
            except KeyboardInterrupt:
                self.console.print("\n\n⚠️  Interrupted by user", style="yellow")
                if Confirm.ask("Do you want to exit?"):
                    break
            except Exception as e:
                self.console.print(f"❌ Unexpected error: {e}", style="red")
                logger.error(f"Unexpected error in chat loop: {e}")
    
    def run_single_query(self, query: str):
        """Run a single query and exit"""
        self.console.print(f"🔍 **Query:** {query}\n", style="bold blue")
        
        result = self.process_query(query)
        if result:
            self.display_response(result)
        else:
            self.console.print("❌ Failed to process query", style="red")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Ask ET - AI-powered Red Hat Emerging Technologies Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/cli.py                    # Start interactive chat
  python src/cli.py -q "What is OpenShift AI?"  # Single query
  python src/cli.py --help             # Show help
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Single query to process (non-interactive mode)'
    )
    
    parser.add_argument(
        '--no-welcome',
        action='store_true',
        help='Skip welcome message'
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = AskETCLI()
    
    # Initialize RAG chain
    if not cli.initialize():
        sys.exit(1)
    
    # Display welcome (unless disabled)
    if not args.no_welcome:
        cli.display_welcome()
    
    # Run appropriate mode
    if args.query:
        cli.run_single_query(args.query)
    else:
        cli.run_interactive()

if __name__ == "__main__":
    main() 