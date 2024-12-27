from bokeh.models import InlineStyleSheet


annotated_files_stylesheet = InlineStyleSheet(
        css="""
        .title {
          font-size: 1.8rem;
          font-weight: bold;
          color: #3498db;
        }

        .bk-btn-group .bk-btn {
            font-size: 1rem;
            color: #222;
            display: list-item;
            padding: 0;
            border: 0;
            margin-left: 1.3rem;
            list-style-type: disc;
            outline: none;
            text-decoration: underline;

            &:hover {
                cursor: pointer;
                background: #fff;
            }
            &:active {
                cursor: pointer;
                background: #fff;
                box-shadow: none;
                outline: none;
            }
        }
    """
    )


annotate_stylesheet = InlineStyleSheet(
        css="""
        .title {
          font-size: 1.8rem;
          font-weight: bold;
          margin: 10px 30px;
          color: #3498db;
          display: block;
          width: 100%;
        }

        .nav {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 10px 0;
            margin-bottom: 10px;
            background: #fff;
            width: 100%;
            border-bottom: 1px solid #eee;
        }

        .nav .bk-row {
            margin-bottom: 10px;
        }

        .filename {
            font-size: 1.2rem;
            font-weight: bold;
            color: #666;
            margin: 10px 30px;
            display: block;
            width: 100%;
        }

        .controls {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 30px;
            background: #fff;
            width: 100%;
        }

        .loader {
          border: 4px solid #e3e3e3;
          border-top: 4px solid #3498db;
          border-radius: 50%;
          width: 20px;
          height: 20px;
          animation: spin 1s linear infinite;
        }

        .bk-btn-group .bk-btn {
            font-size: 1rem;
            color: #222;
            padding: 0;
            border: 0;
            margin-left: 30px;
            outline: none;
            text-decoration: underline;

            &:hover {
                cursor: pointer;
                background: #fff;
            }
            &:active {
                cursor: pointer;
                background: #fff;
                box-shadow: none;
                outline: none;
            }
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }

          100% {
            transform: rotate(360deg);
          }
        }

        .file-list-panel {
            width: 250px;
            background: #f5f5f5;
            padding: 15px;
            border-left: 1px solid #ddd;
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
            color: #3498db;
        }

        .file-item {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            font-size: 0.9rem;
        }

        .file-labeled {
            background: #e1f5e1;
            color: #2c662d;
        }

        .file-unlabeled {
            background: #fff;
            color: #666;
        }

        .main-content {
            margin-right: 250px;
        }

        .file-list-panel .bk-btn {
            margin-bottom: 8px;
            text-align: left;
            white-space: pre-wrap;
            height: auto;
        }

        .file-list-panel .file-labeled.bk-btn {
            background: #e1f5e1;
            color: #2c662d;
        }

        .file-list-panel .file-unlabeled.bk-btn {
            background: #fff;
            color: #666;
        }

        .file-list-panel .bk-btn:hover {
            filter: brightness(0.95);
        }

        .file-list-panel .bk-btn.active {
            border: 2px solid #3498db;
        }
    """
    )