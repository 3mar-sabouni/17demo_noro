/** @odoo-module **/
import { ImageField } from "@web/views/fields/image/image_field";
// import { ImageField, imageField } from '@web/views/fields/image/image_field';
import { patch } from "@web/core/utils/patch";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
let scale = 1;

class ImageDialog extends Component {
  
  zoomIn() {
    // var image = document.getElementById("image");
    //     image.style.transform += "scale(1.2)";
      scale += 0.1;
      document.getElementById('image').style.transform = `scale(${scale})`;
  }

  zoomOut() {
    if (scale > 0.9) { // Assuming 0.5 is the minimum scale you want to allow
      scale -= 0.1;
      document.getElementById('image').style.transform = `scale(${scale})`;
  }

      // scale -= 0.1;
      // document.getElementById('image').style.transform = `scale(${scale})`;
  }
}
ImageDialog.template = xml`
<Dialog title="props.tittle" size="'xl'">
    <t t-if="props.url">
    <div style="position: relative;">
    <div style="display: flex;text-align: center;justify-content: center;align-items: center; height:800px; width:100%;transform-origin: top left;">
        <img id="image" class="img img-fluid" style="height:800px; width:100%;transform-origin: top left; transition: transform 0.3s ease;" alt="Binary file" t-att-src="props.url"/>
        <div style="position:absolute; top: 10px; left: 10px; transform-origin: top left;">
        <button t-on-click="zoomIn">
        <i class="fa fa-search-plus" aria-hidden="true"></i>
        </button>
        <button t-on-click="zoomOut"> <i class="fa fa-search-minus" aria-hidden="true"></i>
    </button>
        </div>
    </div>
</div>
    </t>
    <style>
        .modal-footer {
            display: none;
        }
    </style>
    
</Dialog>`;
ImageDialog.components = { Dialog };
patch(ImageField.prototype, {
 
  async setup() {
    super.setup();
    this.dialogService = useService("dialog");
  },

  fieldImagePreview: function () {
    const name_field = this.props.name;
    if (
      name_field == "image_1024" ||
      name_field == "image_256" ||
      name_field == "image_512" ||
      name_field == "image_128"
    )
      name_field = "image_1920";

    this.dialogService.add(ImageDialog, {
      tittle: this.props.name,
      url: this.getUrl(this.props.name),
    });
  },
  
});
