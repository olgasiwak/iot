export interface Device {
    udid: string;
    mac: string;
    longitude: string;
    latitude: string;
    version_id: number;
    group_id: number;
    id: number;
    icon: any;
}

export interface Group {
    quantity: number;
    description: string;
    configuration: Configuration;
    client_id: number;
    id: number;
}

export interface Configuration {
    lower_threshold: number;
    upper_threshold: number;
}