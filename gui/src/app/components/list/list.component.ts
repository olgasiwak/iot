import { Component } from '@angular/core';
import { Options } from "ng5-slider";
import { ApiComponent } from 'src/app/services/api/api.component';
import { Device, Group } from 'src/app/model';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent {
  groups!: Group[];
  group!: Group;
  devices!: Device[];
  lat = 50.070469317896936;
  lng = 19.993280074662362;

  level: number = 0;
  sliderValue: number = 0;
  options: Options = {
    floor: 0,
    ceil: 100
  };

  changeLevel = false;
  findGroup: any;
  shownId = 0;
  constructor(private api: ApiComponent) { }

  ngOnInit() {
    //pobieramy grupy i sensory z API
    this.getGroups();
  }

  getGroups() {
    this.api.getGroups().subscribe((data) => {
      this.groups = data;
    }, error => { },
      () => {
        this.getDevices();
      });
  }

  getDevices() {
    this.api.getDevices().subscribe((data) => {
      this.devices = data;
    }, error => { }
    );
  }

  clickChange(id: number) {
    this.getGroup(id);
  }

  getGroup(id: number) {
    this.api.getGroup(id).subscribe((data) => {
      this.group = data;
      this.sliderValue = this.group.configuration.upper_threshold * 100
      this.shownId = id;
      this.changeLevel = true;
    });
  }

  saveChanges(id: number) {
    this.api.putGroup(id, this.sliderValue / 100).subscribe(() => {
      this.getGroups();
      this.getDevices();
    },
    error => {},
      () => {
        this.shownId = 0;
        this.changeLevel = false;
      });
  }
}
