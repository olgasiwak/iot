import { Component, OnInit } from '@angular/core';
import { Options } from "ng5-slider";
import { ApiComponent } from 'src/app/services/api/api.component';
import { Device, Group } from 'src/app/model';
@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit {
  groups!: Group[];
  group!: Group;
  devices!: Device[];
  lat = 50.070469317896936;
  lng = 19.993280074662362;
  info = false;
  iconDefault = {
    url: "./assets/images/marker-red.png",
    scaledSize: {
      width: 30,
      height: 42
    }
  }
  level: number = 0;
  sliderValue: number = 0;
  options: Options = {
    floor: 0,
    ceil: 100
  };
  latitude_map!: number;
  changeLevel = false;
  findGroup: any;
  constructor(private api: ApiComponent) {}

  ngOnInit() {
    //pobieramy grupy i sensory z API

    this.getGroups();
    this.getDevices();
  }

  getGroups() {
    this.api.getGroups().subscribe((data)=>{
      this.groups = data;
    
    });
  }

  getDevices() {
    this.api.getDevices().subscribe((data)=>{
      this.devices = data;
      for (let i = 0; i < this.devices.length; i++) {
        this.devices[i]["icon"] = this.iconDefault;
      }
      this.latitude_map = +this.devices[0].latitude
    });
  }


  showInfo(sensor: any) {
    this.changeLevel = false;
    this.info = true;
    for (let i = 0; i < this.devices.length; i++) {
      this.devices[i]["icon"] = this.iconDefault;
    }
    let grupa = this.devices.filter(device => device.group_id === sensor.group_id);
    this.latitude_map = sensor.latitude;
    for (let i = 0; i < grupa.length; i++) {
      grupa[i]["icon"] = {
        url: "./assets/images/marker-blue.png",
        scaledSize: {
          width: 30,
          height: 42
        }
      }
    }
    this.findGroup = this.groups.find((sens: { id: any; }) => sens.id === sensor.group_id);
    this.getGroup(this.findGroup.id);

  }

  clickChange() {
    this.changeLevel = true;
  }

  getGroup(id: number) {
    this.api.getGroup(id).subscribe((data)=>{
      this.group = data;
      this.sliderValue = this.group.configuration.upper_threshold*100
      this.level = this.sliderValue;
      this.options.floor = this.findGroup!.configuration.lower_threshold * 100;
      this.changeLevel = false
    });
  }

  saveChanges() {
    this.api.putGroup(this.findGroup.id, this.sliderValue/100).subscribe(() => {
    },
    error => console.log(error),
    () => {
      this.getGroups();
      this.getDevices();
      this.getGroup(this.findGroup.id)
    });
  }
}
