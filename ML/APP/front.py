import gradio as gr
import requests

def get_resp_model_from_back(input):
    URL='http://127.0.0.1:8000/get_resp/'
    out=requests.get(URL,params={'input':input})
    return out.json()

css = """
<style>
    body {
        background-image: url('image.jpg');
        background-size: cover;
        background-position: center;
    }
</style>
"""

with gr.Blocks() as app:
    gr.Markdown("## ПЕРЕТРИ С ПАЦАНАМИ")
    
    input_get_1 = gr.Textbox(label='изрекай здеся', placeholder='братишка, знаешь Гену Бараду...?')
    output_get = gr.Textbox(label='ответотчка будет тута', placeholder='ща допиздишься, бля...')
    get_btn=gr.Button('ну чё...?')
    get_btn.click(fn=get_resp_model_from_back, inputs=input_get_1, outputs=output_get)

app.launch(server_name="0.0.0.0", server_port=7860)