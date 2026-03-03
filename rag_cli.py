import click
from rag_engine import index_docs, query_docs
import os
import sys

@click.group()
def cli():
    """Finance Tracker RAG CLI - Ask questions about your code and data."""
    pass

@cli.command()
def index():
    """Index the codebase and transaction data."""
    try:
        click.echo("Indexing documents... please wait.")
        index_docs()
        click.echo("Indexing complete! Data stored in .chroma/")
    except Exception as e:
        click.echo(f"Error during indexing: {e}", err=True)

@cli.command()
@click.argument('query')
def ask(query):
    """Ask a question about your code or finances."""
    if not os.path.exists(".chroma"):
        click.echo("Search index not found. Please run 'python rag_cli.py index' first.")
        return
    
    try:
        click.echo(f"Query: {query}")
        click.echo("Thinking...")
        response = query_docs(query)
        click.echo("\n--- Response ---")
        click.echo(response)
    except Exception as e:
        click.echo(f"Error during query: {e}", err=True)

if __name__ == "__main__":
    cli()
