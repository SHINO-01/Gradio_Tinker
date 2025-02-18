import gradio as gr

# Inject JavaScript to detect clicks
head_js = """
<script>
document.addEventListener('click', function(e){
  var t = e.target.closest('.session-item');
  if(!t) return;
  console.log('[DEBUG] Clicked .session-item with index:', t.dataset.index);

  var inp = document.querySelector('#hidden-callback textarea');
  if(inp){
    inp.value = t.dataset.index;
    console.log("[DEBUG] Setting hidden-callback value:", inp.value);
    inp.dispatchEvent(new Event('input', { bubbles: true }));  // Force Gradio to detect input
  }
});
</script>
"""

# Function to process clicks
def debug_load(index):
    print(f"[DEBUG] debug_load() triggered with index = {index}")
    return f"You clicked item: {index}" if index else "No valid selection"

with gr.Blocks(head=head_js) as demo:
    # A hidden textbox that will store clicked values
    hidden_box = gr.Textbox(
        elem_id="hidden-callback",
        visible=False, 
        interactive=True  # Required for event detection
    )
    
    output_box = gr.Textbox(label="Output")

    # Clickable divs
    gr.HTML("""
    <div style="border:1px solid gray; padding:10px;">
      <div class="session-item" data-index="0" style="cursor: pointer; padding: 5px; border: 1px solid black;">
        Item 0
      </div>
      <div class="session-item" data-index="1" style="cursor: pointer; padding: 5px; border: 1px solid black;">
        Item 1
      </div>
    </div>
    """)

    # Ensure Gradio detects updates properly
    hidden_box.input(fn=debug_load, inputs=hidden_box, outputs=output_box)

demo.launch()
