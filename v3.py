import gradio as gr

head_js = """
<script>
document.addEventListener('click', function(e){
  var t = e.target.closest('.session-item');
  if(!t) return;
  console.log('[DEBUG] Clicked .session-item with index:', t.dataset.index);

  var inp = document.querySelector('#hidden-callback');
  if(inp){
    inp.value = t.dataset.index;
    // Important: dispatchEvent('change') pairs with hidden.change(...) in Python
    inp.dispatchEvent(new Event('change', { bubbles: true }));
  }
});
</script>
"""

def debug_load(index):
    print("[DEBUG] debug_load() triggered with index=", index)
    return f"You clicked item: {index}"

with gr.Blocks(head=head_js) as demo:
    # Must match the JS "document.querySelector('#hidden-callback')"
    hidden_box = gr.Textbox(
        elem_id="hidden-callback",
        visible=False,
        interactive=True   # helps on older Gradio versions
    )
    
    output_box = gr.Textbox(label="Output")

    # Provide two clickable divs
    gr.HTML("""
    <div style="border:1px solid gray; padding:10px;">
      <div class="session-item" data-index="0" style="cursor: pointer;">
        Item 0
      </div>
      <div class="session-item" data-index="1" style="cursor: pointer;">
        Item 1
      </div>
    </div>
    """)

    # Listen for 'change' events on hidden_box
    hidden_box.change(debug_load, hidden_box, output_box)

demo.launch()
