import typer
import logging
from dotenv import load_dotenv
from src.presentation.api.dependencies import (
    get_ingestion_service, get_retrieval_service, get_document_agent
)
from src.domain.exceptions import AgenticPlatformError
from src.domain.models.query import QueryRequest

load_dotenv()
logging.basicConfig(level="INFO")

app = typer.Typer(help="Banking Agentic Platform CLI")

@app.command()
def ingest(pdf_path: str = typer.Argument(..., help="Path to PDF file to ingest")):
    """Ingest a PDF document into the vector store."""
    typer.echo(f"Ingesting {pdf_path}...")
    try:
        svc = get_ingestion_service()
        result = svc.ingest(pdf_path)
        typer.echo(typer.style(result, fg=typer.colors.GREEN))
    except AgenticPlatformError as e:
        typer.echo(typer.style(f"Domain Error ({type(e).__name__}): {e}", fg=typer.colors.RED), err=True)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected Error: {e}", fg=typer.colors.RED), err=True)

@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask"),
    conversation_id: str = typer.Option("", "--conversation-id", "-c", help="Conversation ID")
):
    """Ask a single question to the Document Analyst Agent."""
    typer.echo(f"Querying: {question}")
    
    try:
        agent = get_document_agent()
        retrieval_service = get_retrieval_service()
        deps = {"retrieval_service": retrieval_service}
        
        answer = agent.run(question, deps)
        
        # Best-effort source retrieval for CLI display
        query_result = retrieval_service.search(QueryRequest(question=question, top_k=3))
        
        output = f"\nAnswer:\n{answer}"
        if conversation_id:
            output += f"\n[Conversation ID: {conversation_id}]"
            
        typer.echo(typer.style(output, fg=typer.colors.CYAN))
        
        if query_result.contexts:
            typer.echo(typer.style("\nKaynaklar:", fg=typer.colors.YELLOW, bold=True))
            for source in query_result.contexts:
                typer.echo(f"- [Sayfa: {source.page} | Bölüm: {source.section_title} | Skor: {source.score:.3f}]")

    except AgenticPlatformError as e:
        typer.echo(typer.style(f"Domain Error ({type(e).__name__}): {e}", fg=typer.colors.RED), err=True)
    except Exception as e:
        typer.echo(typer.style(f"Unexpected Error: {e}", fg=typer.colors.RED), err=True)

@app.command()
def chat():
    """Start an interactive REPL chat with the Document Analyst Agent."""
    typer.echo("Starting interactive chat. Type 'exit' or 'quit' to stop.")
    typer.echo("Press Ctrl+C to abort safely.")
    
    try:
        agent = get_document_agent()
        retrieval_service = get_retrieval_service()
        deps = {"retrieval_service": retrieval_service}
        
        while True:
            try:
                question = typer.prompt("You")
                if question.lower() in ('exit', 'quit'):
                    typer.echo("Goodbye!")
                    break
                    
                answer = agent.run(question, deps)
                typer.echo(typer.style(f"\nAgent: {answer}\n", fg=typer.colors.CYAN))
                
                # Fetch and print sources in chat as well
                query_result = retrieval_service.search(QueryRequest(question=question, top_k=3))
                if query_result.contexts:
                    typer.echo(typer.style("Kaynaklar:", fg=typer.colors.YELLOW, bold=True))
                    for source in query_result.contexts:
                        typer.echo(f"- [Sayfa: {source.page} | Bölüm: {source.section_title} | Skor: {source.score:.3f}]")
                typer.echo("\n" + "-"*40)
                
            except typer.Abort:
                typer.echo("\nChat aborted.")
                break
            except KeyboardInterrupt:
                typer.echo("\nChat interrupted. Goodbye!")
                break
            except AgenticPlatformError as e:
                typer.echo(typer.style(f"Domain Error ({type(e).__name__}): {e}\n", fg=typer.colors.RED), err=True)
            except Exception as e:
                typer.echo(typer.style(f"Unexpected Error: {e}\n", fg=typer.colors.RED), err=True)
                
    except Exception as init_err:
        typer.echo(typer.style(f"Failed to initialize chat: {init_err}", fg=typer.colors.RED), err=True)

if __name__ == "__main__":
    app()
