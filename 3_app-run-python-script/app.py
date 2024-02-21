## Sample application runtime

## Sample implementation 1
!streamlit run 2_app/app.py --server.port $CDSW_APP_PORT --server.address 127.0.0.1

## Sample implementation 2
import os

def main():
    demo.launch(
        server_name='127.0.0.1',
        server_port=int(os.getenv('CDSW_APP_PORT')))
    
if __name__ == "__main__":
    main()