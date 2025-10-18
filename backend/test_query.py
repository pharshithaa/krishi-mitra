#!/usr/bin/env python3
"""
Interactive Query Testing Tool for KrishiMitra RAG
"""

import requests
import sys
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class RAGTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/rag"

    def check_health(self) -> bool:
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=15)
            if response.status_code == 200 or response.status_code == 503:
                data = response.json()
                print(f"{Colors.GREEN}✅ API is running{Colors.END}")
                print(f"{Colors.CYAN}📊 Status:{Colors.END}")
                print(f"  - Overall: {data.get('status', 'unknown')}")
                print(f"  - Pinecone: {data.get('pinecone', 'unknown')}")
                print(f"  - LangGraph: {data.get('langgraph', 'unknown')}")

                # Check details if available
                details = data.get("details", {})
                if details:
                    gen_status = details.get("generation", {})
                    if isinstance(gen_status, dict):
                        print(f"  - Generation: {gen_status.get('status', 'unknown')}")

                    # Show vector count
                    retrieval = details.get("retrieval", {})
                    if isinstance(retrieval, dict) and "vector_count" in retrieval:
                        print(f"  - Vectors in Pinecone: {retrieval['vector_count']}")

                return response.status_code == 200
            else:
                print(
                    f"{Colors.RED}❌ API returned status {response.status_code}{Colors.END}"
                )
                return False
        except requests.exceptions.ConnectionError:
            print(
                f"{Colors.RED}❌ Cannot connect to API at {self.base_url}{Colors.END}"
            )
            print(
                f"{Colors.YELLOW}💡 Make sure the server is running: uvicorn main:app --reload --port 8000{Colors.END}"
            )
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
            return False

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Send a query to the RAG API"""
        try:
            payload = {"query": question, "top_k": top_k}

            print(f"\n{Colors.CYAN}🔍 Querying...{Colors.END}")
            response = requests.post(f"{self.api_url}/query", json=payload, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"{Colors.RED}❌ Query failed with status {response.status_code}{Colors.END}"
                )
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"{Colors.RED}❌ Query timed out (>30s){Colors.END}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
            return None

    def display_result(self, result: Dict[str, Any]):
        """Display query result in a formatted way"""
        if not result:
            return

        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}📝 ANSWER{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 80}{Colors.END}\n")

        answer = result.get("answer", "No answer generated")
        print(f"{Colors.BOLD}{answer}{Colors.END}\n")

        # Display performance metrics
        print(f"{Colors.CYAN}⏱️  Performance Metrics:{Colors.END}")
        print(f"  • Total Latency: {result.get('latency_ms', 0):.0f}ms")

        node_latencies = result.get("node_latencies", {})
        if node_latencies:
            print(f"  • Embed: {node_latencies.get('embed_ms', 0):.0f}ms")
            print(f"  • Retrieve: {node_latencies.get('retrieve_ms', 0):.0f}ms")
            print(f"  • Generate: {node_latencies.get('generate_ms', 0):.0f}ms")

        # Display sources
        sources = result.get("sources", [])
        if sources:
            print(
                f"\n{Colors.YELLOW}📚 Sources ({len(sources)} documents):{Colors.END}"
            )
            for i, source in enumerate(sources, 1):
                print(
                    f"\n  {Colors.BOLD}[{i}] {source.get('title', 'Untitled')}{Colors.END}"
                )
                print(f"      Score: {source.get('score', 0):.4f}")
                if "metadata" in source:
                    metadata = source["metadata"]
                    if "category" in metadata:
                        print(f"      Category: {metadata['category']}")
                    if "page" in metadata:
                        print(f"      Page: {metadata['page']}")

                # Show preview of content
                content = source.get("content", "")
                if content:
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"      Preview: {preview}")

        # Display retrieved chunks (optional, collapsed by default)
        chunks = result.get("retrieved_chunks", [])
        if chunks:
            print(f"\n{Colors.CYAN}📄 Retrieved Chunks: {len(chunks)}{Colors.END}")
            print(
                f"{Colors.YELLOW}💡 Tip: These are the text chunks used to generate the answer{Colors.END}"
            )

        print(f"\n{Colors.GREEN}{'=' * 80}{Colors.END}\n")

    def interactive_mode(self):
        """Run in interactive mode"""
        print(
            f"\n{Colors.BOLD}{Colors.HEADER}🌾 KrishiMitra RAG - Interactive Query Tool{Colors.END}\n"
        )

        # Check health first
        if not self.check_health():
            return

        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}Commands:{Colors.END}")
        print("  • Type your question and press Enter")
        print("  • Type 'quit' or 'exit' to stop")
        print("  • Type 'health' to check API status")
        print("  • Type 'examples' to see sample questions")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.END}\n")

        while True:
            try:
                question = input(
                    f"{Colors.BOLD}{Colors.BLUE}❓ Your question: {Colors.END}"
                ).strip()

                if not question:
                    continue

                if question.lower() in ["quit", "exit", "q"]:
                    print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.END}\n")
                    break

                if question.lower() == "health":
                    self.check_health()
                    continue

                if question.lower() == "examples":
                    self.show_examples()
                    continue

                # Query the API
                result = self.query(question)
                if result:
                    self.display_result(result)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.END}\n")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

    def show_examples(self):
        """Show example questions"""
        print(f"\n{Colors.YELLOW}📋 Example Questions:{Colors.END}\n")
        examples = [
            "What crops are best for kharif season?",
            "How do I control pests in rice cultivation?",
            "What is the best fertilizer for wheat?",
            "When should I plant tomatoes?",
            "How to improve soil health?",
            "What are the symptoms of leaf blight?",
            "Best irrigation practices for cotton",
            "How to store harvested crops?",
        ]
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Query Testing Tool for KrishiMitra RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_query.py
  
  # Single query
  python test_query.py -q "What crops are best for kharif season?"
  
  # Custom API URL
  python test_query.py --url http://localhost:8000
        """,
    )

    parser.add_argument(
        "-q", "--query", type=str, help="Single query to test (non-interactive mode)"
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)",
    )

    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of chunks to retrieve (default: 5)"
    )

    args = parser.parse_args()

    tester = RAGTester(base_url=args.url)

    if args.query:
        # Single query mode
        if not tester.check_health():
            sys.exit(1)

        print(f"\n{Colors.BOLD}Question:{Colors.END} {args.query}\n")
        result = tester.query(args.query, top_k=args.top_k)
        if result:
            tester.display_result(result)
    else:
        # Interactive mode
        tester.interactive_mode()


if __name__ == "__main__":
    main()
