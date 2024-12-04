import { Component, Input } from '@angular/core';

@Component({
  selector: 'hint-tooltip',
  standalone: true,
  templateUrl: './hint-tooltip.component.html',
})

export class HintTooltipComponent {
    @Input() tooltipTxt: string = ''
}