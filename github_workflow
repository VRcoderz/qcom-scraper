name: Quick Commerce News Scraper

on:
  # Run daily at 6 AM UTC
  schedule:
    - cron: '0 6 * * *'
  
  # Allow manual triggering with timeframe selection
  workflow_dispatch:
    inputs:
      timeframe:
        description: 'Select timeframe for news scraping'
        required: true
        default: '7d'
        type: choice
        options:
          - '6h'
          - '12h'
          - '24h'
          - '2d'
          - '3d'
          - '7d'
          - '14d'
          - '30d'
          - '60d'
          - '90d'
          - 'custom'
      custom_days:
        description: 'Number of days (only for custom timeframe)'
        required: false
        default: '7'
        type: string

jobs:
  scrape-news:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run news scraper
      env:
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        SCRAPE_TIMEFRAME: ${{ github.event.inputs.timeframe || '24h' }}
        CUSTOM_DAYS_BACK: ${{ github.event.inputs.custom_days || '7' }}
      run: |
        python scraper.py --timeframe ${{ github.event.inputs.timeframe || '24h' }}
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: quick-commerce-news-${{ github.event.inputs.timeframe || '24h' }}-${{ github.run_number }}
        path: |
          quick_commerce_news_*.txt
          quick_commerce_news_*.json
        retention-days: 30
    
    - name: Commit and push results
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add quick_commerce_news_*.txt quick_commerce_news_*.json
        
        # Check if there are any changes to commit
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          TIMEFRAME="${{ github.event.inputs.timeframe || '24h' }}"
          git commit -m "Add quick commerce news update ($TIMEFRAME) - $(date '+%Y-%m-%d %H:%M:%S')"
          git push
        fi
    
    - name: Create Release
      if: github.event_name == 'schedule' || github.event.inputs.timeframe == '7d' || github.event.inputs.timeframe == '30d'
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: news-${{ github.event.inputs.timeframe || '24h' }}-${{ github.run_number }}
        release_name: Quick Commerce News (${{ github.event.inputs.timeframe || '24h' }}) - ${{ github.run_number }}
        body: |
          Automated quick commerce industry news scraping results.
          
          📅 Generated: ${{ github.run_date }}
          ⏰ Timeframe: ${{ github.event.inputs.timeframe || '24h' }}
          🔍 Articles collected from 25+ Indian news sources
          📊 Data available in both text and JSON formats
        draft: false
        prerelease: false

    - name: Upload Release Assets
      if: github.event_name == 'schedule' || github.event.inputs.timeframe == '7d' || github.event.inputs.timeframe == '30d'
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: quick_commerce_news_*.txt
        asset_name: quick_commerce_news_${{ github.event.inputs.timeframe || '24h' }}.txt
        asset_content_type: text/plain

# Additional workflows for different schedules
  hourly-updates:
    runs-on: ubuntu-latest
    # Run every 3 hours for breaking news
    if: github.event_name == 'schedule'
    strategy:
      matrix:
        timeframe: ['6h']
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run hourly scraper
      env:
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        SCRAPE_TIMEFRAME: ${{ matrix.timeframe }}
      run: |
        python scraper.py --timeframe ${{ matrix.timeframe }}
    
    - name: Upload hourly artifacts
      uses: actions/upload-artifact@v3
      with:
        name: quick-commerce-breaking-news-${{ github.run_number }}
        path: |
          quick_commerce_news_*hours*.txt
          quick_commerce_news_*hours*.json
        retention-days: 7name: Quick Commerce News Scraper

on:
  # Run daily at 6 AM UTC
  schedule:
    - cron: '0 6 * * *'
  
  # Allow manual triggering
  workflow_dispatch:
    inputs:
      days_back:
        description: 'Number of days to look back for news'
        required: false
        default: '7'
        type: string

jobs:
  scrape-news:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run news scraper
      env:
        NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        SCRAPE_DAYS_BACK: ${{ github.event.inputs.days_back || '7' }}
      run: |
        python scraper.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: quick-commerce-news-${{ github.run_number }}
        path: |
          quick_commerce_news_*.txt
          quick_commerce_news_*.json
        retention-days: 30
    
    - name: Commit and push results
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add quick_commerce_news_*.txt quick_commerce_news_*.json
        
        # Check if there are any changes to commit
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Add quick commerce news update - $(date '+%Y-%m-%d %H:%M:%S')"
          git push
        fi
    
    - name: Create Release
      if: github.event_name == 'schedule'
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: news-${{ github.run_number }}
        release_name: Quick Commerce News - ${{ github.run_number }}
        body: |
          Automated quick commerce industry news scraping results.
          
          📅 Generated: ${{ github.run_date }}
          🔍 Articles collected from multiple sources
          📊 Data available in both text and JSON formats
        draft: false
        prerelease: false

    - name: Upload Release Assets
      if: github.event_name == 'schedule'
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: quick_commerce_news_*.txt
        asset_name: quick_commerce_news.txt
        asset_content_type: text/plain
