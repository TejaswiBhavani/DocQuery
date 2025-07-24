import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

class DocumentRecord(Base):
    """Database model for uploaded documents."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    chunk_count = Column(Integer)
    processing_time = Column(Float)  # in seconds
    search_type = Column(String(100))  # which search engine was used

class QueryRecord(Base):
    """Database model for user queries."""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    original_query = Column(Text, nullable=False)
    parsed_query = Column(JSON)  # structured extracted data
    query_time = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds

class AnalysisRecord(Base):
    """Database model for AI analysis results."""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, nullable=False)
    decision = Column(String(50))  # Approved/Rejected
    amount = Column(String(100))  # monetary amount if applicable
    justification = Column(Text)
    clause_reference = Column(Text)
    confidence = Column(String(20))  # High/Medium/Low
    relevant_chunks = Column(JSON)  # list of relevant document sections
    ai_model_used = Column(String(50))
    analysis_time = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds

class DatabaseManager:
    """Manages database operations for the document analysis system."""
    
    def __init__(self):
        """Initialize database connection and create tables."""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL environment variable not found")
        
        try:
            self.engine = create_engine(database_url, echo=False)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine, checkfirst=True)
            
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
        except Exception as e:
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def save_document(self, filename: str, file_size: int, chunk_count: int, 
                     processing_time: float, search_type: str) -> int:
        """
        Save document upload information.
        
        Args:
            filename: Name of uploaded file
            file_size: Size of file in bytes
            chunk_count: Number of text chunks created
            processing_time: Time taken to process document
            search_type: Type of search engine used
            
        Returns:
            Document ID
        """
        try:
            document = DocumentRecord(
                filename=filename,
                file_size=file_size,
                chunk_count=chunk_count,
                processing_time=processing_time,
                search_type=search_type
            )
            
            self.session.add(document)
            self.session.commit()
            
            return document.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save document record: {str(e)}")
    
    def save_query(self, document_id: int, original_query: str, 
                  parsed_query: Dict, processing_time: float) -> int:
        """
        Save user query information.
        
        Args:
            document_id: ID of associated document
            original_query: Original user query text
            parsed_query: Structured extracted data
            processing_time: Time taken to process query
            
        Returns:
            Query ID
        """
        try:
            query = QueryRecord(
                document_id=document_id,
                original_query=original_query,
                parsed_query=parsed_query,
                processing_time=processing_time
            )
            
            self.session.add(query)
            self.session.commit()
            
            return query.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save query record: {str(e)}")
    
    def save_analysis(self, query_id: int, decision: str, amount: Optional[str],
                     justification: str, clause_reference: str, confidence: str,
                     relevant_chunks: List[str], ai_model: str, processing_time: float) -> int:
        """
        Save AI analysis results.
        
        Args:
            query_id: ID of associated query
            decision: Analysis decision (Approved/Rejected)
            amount: Monetary amount if applicable
            justification: Explanation of decision
            clause_reference: Referenced clauses
            confidence: Confidence level
            relevant_chunks: Relevant document sections
            ai_model: AI model used for analysis
            processing_time: Time taken for analysis
            
        Returns:
            Analysis ID
        """
        try:
            analysis = AnalysisRecord(
                query_id=query_id,
                decision=decision,
                amount=amount,
                justification=justification,
                clause_reference=clause_reference,
                confidence=confidence,
                relevant_chunks=relevant_chunks,
                ai_model_used=ai_model,
                processing_time=processing_time
            )
            
            self.session.add(analysis)
            self.session.commit()
            
            return analysis.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save analysis record: {str(e)}")
    
    def get_query_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent query history with results.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of query history records
        """
        try:
            # Join queries with their analysis results
            results = self.session.query(
                QueryRecord.id,
                QueryRecord.original_query,
                QueryRecord.parsed_query,
                QueryRecord.query_time,
                AnalysisRecord.decision,
                AnalysisRecord.amount,
                AnalysisRecord.confidence,
                DocumentRecord.filename
            ).join(
                AnalysisRecord, QueryRecord.id == AnalysisRecord.query_id
            ).join(
                DocumentRecord, QueryRecord.document_id == DocumentRecord.id
            ).order_by(
                QueryRecord.query_time.desc()
            ).limit(limit).all()
            
            history = []
            for result in results:
                history.append({
                    'query_id': result.id,
                    'query': result.original_query,
                    'parsed_query': result.parsed_query,
                    'decision': result.decision,
                    'amount': result.amount,
                    'confidence': result.confidence,
                    'document': result.filename,
                    'timestamp': result.query_time.isoformat()
                })
            
            return history
            
        except Exception as e:
            raise Exception(f"Failed to get query history: {str(e)}")
    
    def get_analytics(self) -> Dict:
        """
        Get system analytics and statistics.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            # Count total documents, queries, and decisions
            total_docs = self.session.query(DocumentRecord).count()
            total_queries = self.session.query(QueryRecord).count()
            
            approved_count = self.session.query(AnalysisRecord).filter(
                AnalysisRecord.decision == 'Approved'
            ).count()
            
            rejected_count = self.session.query(AnalysisRecord).filter(
                AnalysisRecord.decision == 'Rejected'
            ).count()
            
            # Get average processing times
            avg_processing_time = self.session.query(
                AnalysisRecord.processing_time
            ).all()
            
            avg_time = sum(t[0] for t in avg_processing_time if t[0]) / len(avg_processing_time) if avg_processing_time else 0
            
            return {
                'total_documents': total_docs,
                'total_queries': total_queries,
                'total_analyses': approved_count + rejected_count,
                'approved_decisions': approved_count,
                'rejected_decisions': rejected_count,
                'approval_rate': (approved_count / (approved_count + rejected_count)) * 100 if (approved_count + rejected_count) > 0 else 0,
                'average_processing_time': round(avg_time, 2)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get analytics: {str(e)}")
    
    def search_queries(self, search_term: str, limit: int = 20) -> List[Dict]:
        """
        Search through query history.
        
        Args:
            search_term: Term to search for
            limit: Maximum results to return
            
        Returns:
            List of matching queries
        """
        try:
            results = self.session.query(
                QueryRecord.id,
                QueryRecord.original_query,
                QueryRecord.query_time,
                AnalysisRecord.decision,
                DocumentRecord.filename
            ).join(
                AnalysisRecord, QueryRecord.id == AnalysisRecord.query_id
            ).join(
                DocumentRecord, QueryRecord.document_id == DocumentRecord.id
            ).filter(
                QueryRecord.original_query.ilike(f'%{search_term}%')
            ).order_by(
                QueryRecord.query_time.desc()
            ).limit(limit).all()
            
            matches = []
            for result in results:
                matches.append({
                    'query_id': result.id,
                    'query': result.original_query,
                    'decision': result.decision,
                    'document': result.filename,
                    'timestamp': result.query_time.isoformat()
                })
            
            return matches
            
        except Exception as e:
            raise Exception(f"Failed to search queries: {str(e)}")
    
    def close(self):
        """Close database session."""
        self.session.close()