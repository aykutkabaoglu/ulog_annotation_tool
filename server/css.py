from bokeh.models import InlineStyleSheet


annotated_files_stylesheet = InlineStyleSheet(
        css="""
        body {
            background: #1a1a1a;
            color: #e0e0e0;
        }

        .title {
          font-size: 1.8rem;
          font-weight: bold;
          color: #5dade2;
        }

        .bk-btn-group .bk-btn {
            font-size: 1rem;
            color: #e0e0e0;
            display: list-item;
            padding: 0;
            border: 0;
            margin-left: 1.3rem;
            list-style-type: disc;
            outline: none;
            text-decoration: underline;
            background: transparent;

            &:hover {
                cursor: pointer;
                background: #404040;
            }
            &:active {
                cursor: pointer;
                background: #404040;
                box-shadow: none;
                outline: none;
            }
        }
    """
    )


annotate_stylesheet = InlineStyleSheet(
        css="""
        /* Global styles for the entire page */
        :root {
            background: #1a1a1a !important;
        }
        
        body {
            background: #1a1a1a !important;
            color: #e0e0e0;
        }

        /* Main content area */
        .main-content {
            background: #1a1a1a !important;
            min-height: 100vh;
        }

        /* Ensure Bokeh's container is also dark */
        .bk-root {
            background: #1a1a1a !important;
        }

        .title {
          font-size: 1.8rem;
          font-weight: bold;
          margin: 10px 30px;
          color: #5dade2;
          display: block;
          width: 100%;
        }

        .nav {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 10px 0;
            margin-bottom: 10px;
            background: #2d2d2d;
            width: 100%;
            border-bottom: 1px solid #404040;
        }

        .filename {
            font-size: 1.2rem;
            font-weight: bold;
            color: #e0e0e0;
            margin: 10px 30px;
            display: block;
            width: 100%;
        }

        .controls {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 30px;
            background: #2d2d2d;
            width: 100%;
        }

        .loader {
          border: 4px solid #404040;
          border-top: 4px solid #5dade2;
          border-radius: 50%;
          width: 20px !important;
          height: 20px !important;
          animation: spin 1s linear infinite;
          display: inline-block;
          visibility: visible !important;
          margin: 0 10px;
        }

        .file-list-panel {
            width: 250px;
            background: #2d2d2d;
            padding: 15px;
            border-left: 1px solid #404040;
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            right: 0;
            top: 0;
        }

        .file-list-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #5dade2;
        }

        .file-item {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            font-size: 0.9rem;
        }

        .file-labeled {
            background: #1e4620;
            color: #a8e6a8;
        }

        .file-unlabeled {
            background: #2d2d2d;
            color: #e0e0e0;
        }

        .file-list-panel .bk-btn {
            margin-bottom: 8px;
            text-align: left;
            white-space: pre-wrap;
            height: auto;
            background: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #404040;
        }

        .file-list-panel .file-labeled.bk-btn {
            background: #1e4620;
            color: #a8e6a8;
        }

        .file-list-panel .file-unlabeled.bk-btn {
            background: #2d2d2d;
            color: #e0e0e0;
        }

        .file-list-panel .bk-btn:hover {
            background: #404040;
        }

        .file-list-panel .bk-btn.active {
            border: 2px solid #5dade2;
        }

        /* Style for input elements */
        input, select {
            background: #2d2d2d !important;
            color: #e0e0e0 !important;
            border: 1px solid #404040 !important;
        }

        /* Style for buttons */
        .bk-btn {
            background: #2d2d2d !important;
            color: #e0e0e0 !important;
            border: 1px solid #404040 !important;
        }

        .bk-btn:hover {
            background: #404040 !important;
        }

        @keyframes spin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }
    """
    )