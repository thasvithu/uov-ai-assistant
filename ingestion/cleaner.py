"""
Text cleaning utilities for document processing.
"""

import re
from typing import Optional


def clean_text(text: str, preserve_newlines: bool = True) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        preserve_newlines: Whether to preserve paragraph breaks
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    
    if preserve_newlines:
        # Normalize line breaks (keep paragraph structure)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
    else:
        # Replace all newlines with spaces
        text = text.replace('\n', ' ')
    
    # Remove special characters but keep basic punctuation
    # Keep: letters, numbers, basic punctuation, Tamil, Sinhala characters
    text = re.sub(r'[^\w\s.,!?;:()\-\u0B80-\u0BFF\u0D80-\u0DFF]', '', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip()


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text containing URLs
        
    Returns:
        Text with URLs removed
    """
    # Remove http/https URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    return text


def remove_email_addresses(text: str) -> str:
    """
    Remove email addresses from text.
    
    Args:
        text: Text containing email addresses
        
    Returns:
        Text with email addresses removed
    """
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    return text


def clean_document_text(
    text: str,
    remove_urls_flag: bool = False,
    remove_emails_flag: bool = False,
    preserve_newlines: bool = True
) -> str:
    """
    Comprehensive text cleaning for documents.
    
    Args:
        text: Raw document text
        remove_urls_flag: Whether to remove URLs
        remove_emails_flag: Whether to remove email addresses
        preserve_newlines: Whether to preserve paragraph breaks
        
    Returns:
        Cleaned text
    """
    if remove_urls_flag:
        text = remove_urls(text)
    
    if remove_emails_flag:
        text = remove_email_addresses(text)
    
    text = clean_text(text, preserve_newlines)
    text = normalize_whitespace(text)
    
    return text
