import React, { Component } from 'react';
import {
  Polyline,
  Rectangle,
  Map,
  LayerGroup,
  LayersControl,
} from 'react-leaflet';
import { 
  Table,
  Button,
  Upload,
  Icon,
  message
} from 'antd';
import L from 'leaflet';
import DataService from '../../services/data_service';
import './evaluation.style.scss';

const { BaseLayer, Overlay } = LayersControl;
class EvaluationView extends Component {
  constructor(props) {
    super(props);
    this.props = props;
    this.state = {
      inputJson: '{"ENTRANCE":[[1,2,3,4]]}',
      evaluationResult: `{"align_score": 0,
        "desired_size": 0,
        "hallway_access_score": 0,
        "hallway_number": 0,
        "lounge_score": 0,
        "meet_score": 0,
        "size_score": ${JSON.stringify({"CIRC": 0.0,
                    "OPERATE": 0.0,
                    "WORK": 0.0,
                    "ENTRANCE": 0.0,
                    "MEET": 0.0,
                    "WASH": 0.0,
                    "OBS": 0.0})},
        "total_area": 0,
        "total_usable_area": 0,
        "total_used_area": 0,
        "work_ext_score": 0}`
    };
    this.onChange = this.onChange.bind(this);
  }

  componentDidUpdate(prevProps, prevState) {
    const { inputJson } = this.state;
    if (prevState.inputJson !== inputJson) {
      DataService.fetchEvaluationResult(inputJson).then((response) => {
        this.setState({
          evaluationResult: JSON.stringify(response),
        });
      });
    }
  }

  onChange(info) {
    if (info.file.status !== 'uploading') {
      // console.log(info.file, info.fileList);
      const reader = new FileReader();
      reader.onload = (e) => {
        this.setState({
          inputJson: e.target.result,
        });
      };
      reader.readAsText(info.file.originFileObj);
    }
    if (info.file.status === 'done') {
      message.success(`${info.file.name} file uploaded successfully`);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  }

  parseJsonToArr = (file) => {
    const floorData = JSON.parse(file);
    const recData = [];
    const colorDict = {
      CIRC: 'rgba(255, 247, 220, 255)',
      WORK: 'rgba(227, 243, 246, 255)',
      WASH: 'rgba(195, 195, 195, 255)',
      OPERATE: 'rgba(254, 176, 177, 255)',
      MEET: 'rgba(184, 240, 218, 255)',
      ENTRANCE: 'rgba(255, 210, 118, 255)',
      EMPTY: 'rgba(255, 255, 255, 255)',
      OTHER: 'rgba(0, 0, 0, 255)',
    };

    Object.entries(floorData).forEach((val) => {
      val[1].forEach((item) => {
        const tmp = item.map((it) => (Math.round(it)));
        tmp.push(colorDict[val[0]]);
        if (val[0] === 'CIRC') {
          recData.unshift(tmp);
        } else {
          recData.push(tmp);
        }
      });
    });
    return recData;
  };

  render() {
    const { inputJson, evaluationResult } = this.state;
    const rectangleArr = this.parseJsonToArr(inputJson);
    const props = {
      style: { marginRight: '20px' },
      name: 'file',
      action: '//jsonplaceholder.typicode.com/posts/',
      onChange: this.onChange,
      multiple: false,
    };
    // Setting grid cell size, grid number, and minimum zoom value.
    // 500 x 500 grid total with each grid cell as 128 x 128 pixels.
    const grid_size = 128;
    const num_grid = 500;
    const min_zoom = -5;
    // Square grid with range [min_v, max_v] for x, y.
    const min_v = -(num_grid / 5) * grid_size;
    const max_v = 4 * (num_grid / 5) * grid_size;
    const mid_v = (min_v + max_v) / 2;
    const min_bounds = [min_v, min_v];
    const max_bounds = [max_v, max_v];
    const center = [mid_v, mid_v];
    const gridArr = new Array(num_grid+1).fill(0);
    let key = 0;
    // Drawing the gridlines on the plot.
    const gridRow = gridArr.map((val, idx) => (<Polyline positions={[[idx * grid_size + min_v, min_v],
      [idx * grid_size + min_v, max_v]]} color="black" weight={0.05 + 0.05 * (idx % 10 === 0)} key={key++} />));
    // positions.bringToFront(); // Doesn't work.
    const gridCol = gridArr.map((val, idx) => (<Polyline positions={[[min_v, idx * grid_size + min_v],
      [max_v, idx * grid_size + min_v]]} color="black" weight={0.05 + 0.05 * (idx % 10 === 0)} key={key++} />));
    // Plotting floorplan with each square foot as one grid square.
    const rectangle = rectangleArr.map((val) => (
      <Rectangle
        bounds={[[val[1] * grid_size, val[0] * grid_size], [val[3] * grid_size, val[2] * grid_size]]}
        color={val[4]}
        fillOpacity={1}
        key={key++}
        stroke={false}
      />
    ));
    const floor_cols = [
      {
        title: 'Key Stats',
        dataIndex: 'usf',
        width: 200,
        key: 'usf',
      },
      {
        title: 'Area',
        dataIndex: 'floor_area',
        width: 200,
        key: 'floor_area',
      },
    ];
    const area_cols = [
      {
        title: 'Zone Types',
        dataIndex: 'zone',
        width: 200,
        key: 'zone',
      },
      {
        title: 'Desired Target Area',
        dataIndex: 'areaO',
        width: 200,
        key: 'area0',
      },
      {
        title: 'Actual Area',
        dataIndex: 'area1',
        width: 200,
        key: 'area1',
      }
    ];
    const columns = [
      {
        title: 'Constraints',
        dataIndex: 'constraints',
        width: 200,
        key: 'constraints',
      },
      {
        title: 'Check_Origin',
        dataIndex: 'checkO',
        width: 200,
        key: 'checkO',
      }
    ];
    const result = JSON.parse(evaluationResult);
    const datasourceFloor = [
        {
        usf: 'Total Area',
        floor_area: `${result.total_area} sq.ft`,
        },
        {
        usf: 'Total Usable Area',
        floor_area: `${result.total_usable_area} sq.ft`,
        },
        {
        usf: 'Total Used Area',
        floor_area: `${result.total_used_area} sq.ft`,
        },
    ];
    // Hardcoded target area percentages for [WORK, MEET, ENTRANCE, CIRCULATE].
    // TODO: Calculate actual area of each zone (returned from backend? or do in frontend).
    const target = [0.54, 0.06, 0.10, 0.20];
    console.log(result.size_score);
    // alert(typeof result.size_score);
    let dict = result.size_score;
    if (typeof dict === 'string') {
      dict = dict.replace(/'/g, '"');
      dict = JSON.parse(dict);
    }
    const datasourceArea = [
      {
        key: '1',
        zone: 'WORK',
        areaO: `${target[0]*result.total_usable_area} sq.ft`,
        area1: `${-dict['WORK']} sq.ft`,
      },
      {
        key: '2',
        zone: 'MEET',
        areaO: `${target[1]*result.total_usable_area} sq.ft`,
        area1: `${-dict['MEET']} sq.ft`,
      },
      {
        key: '3',
        zone: 'ENTRANCE',
        areaO: `${target[2]*result.total_usable_area} sq.ft`,
        area1: `${-dict['ENTRANCE']} sq.ft`,
      },
      {
        key: '4',
        zone: 'CIRCULATE',
        areaO: `${target[3]*result.total_usable_area} sq.ft`,
        area1: `${-dict['CIRC']} sq.ft`,
      }
    ];
    const datasourceGen = [
      {
        key: '1',
        constraints: 'Enclosure: All the Zones should be located inside of the floor plan boundary.',
        checkO: 'True',
      },
      {
        key: '2',
        constraints: 'Non-overlapping: There is no overlap between zones.',
        checkO: 'True',
      },
      {
        key: '3',
        constraints: 'Full-coverage: The zones should collectively cover all the floor area.',
        checkO: `${(result.total_usable_area - result.total_used_area).toString()} sq.ft have not been used`,
      },
      {
        key: '4',
        constraints: 'Accessibility: All zones can access to circulate.',
        checkO: 'True',
      }
    ];

    let lounge_scores = result.lounge_score;
    if (typeof lounge_scores === 'string') {
      lounge_scores = lounge_scores.replace(/'/g, '"');
      lounge_scores = JSON.parse(lounge_scores);
    }
    const datasourceZone = [
      {
        key: '1',
        constraints: 'CIRCULATE is a minimum of 4 ft. wide.',
        checkO: 'True'
      },
      {
        key: '2',
        constraints: 'ENTRANCE LOUNGE should be close to the elevator lobby and have good views/daylight.',
        checkO: `Access to elevator: ${lounge_scores['touch_core']}; Access to views: ${lounge_scores['touch_gv']}`
      },
      {
        key: '3',
        constraints: 'Maximize WORK area along the exterior boundary.',
        checkO: `Exterior workspace is ${result.work_ext_score} sq.ft`
      },
      {
        key: '4',
        constraints: 'Minimize corners/turns of CIRCULATE.',
        checkO: `There are ${result.hallway_number} corners.`
      },
      {
        key: '5',
        constraints: 'CIRCULATE should connect to floor exits and elevators.',
        checkO: 'True'
      },
      {
        key: '6',
        constraints: 'Conference rooms are preferred to be located alongside the core.',
        checkO: 'True'
      },
      {
        key: '7',
        constraints: 'Phone booths and printers are better distributed across a floor.',
        checkO: 'True'
      },
    ];

    // Sets so that the user can turn grid on/off (perhaps can add multiple sizes of grid).
    // TODO: fix the grid display over the floorplan (Sometimes only part of it is gridded)
    return (
      <div id="page-container">
        <div id="title">
          <h2 id="title-text">Evaluation Demo</h2>
        </div>
        <div id="load-image">
          <Map className="map" crs={L.CRS.Simple} center={center} maxBounds={[min_bounds, max_bounds]}
               zoom={min_zoom} minZoom={min_zoom} maxZoom={0} animate={true} layers={[]}>
            <LayersControl position="topright" autoZIndex={true} sortLayers={true}>
              <BaseLayer checked name="Floorplan">
                <LayerGroup pane={'tilePane'}>
                  {rectangle}
                </LayerGroup>
              </BaseLayer>
              <Overlay name="Grid (1ft. x 1ft.)">
                <LayerGroup>
                  {gridRow}
                  {gridCol}
                </LayerGroup>
              </Overlay>
            </LayersControl>
          </Map>
          <div id="map-symbols">
            <span id="CIRC-symbol"></span>
            <span id="map-symbol-text"> CIRC </span>
            <span id="WORK-symbol"></span>
            <span id="map-symbol-text"> WORK </span>
            <span id="WASH-symbol"></span>
            <span id="map-symbol-text"> WASH </span>
            <span id="OPERATE-symbol"></span>
            <span id="map-symbol-text"> OPERATE </span>
            <span id="MEET-symbol"></span>
            <span id="map-symbol-text"> MEET </span>
            <span id="ENTRANCE-symbol"></span>
            <span id="map-symbol-text"> ENTRANCE </span>
            <span id="OTHER-symbol"></span>
            <span id="map-symbol-text"> OTHER </span>
          </div>
          <div id="operation">
            <Upload {...props}>
              <Button type="primary" size="large">
                <Icon type="upload" />
                Upload a plan
              </Button>
            </Upload>
          </div>
        </div>
        <div id="result">
          <div id="result-title">
            <h3 id="title-text">Evaluation Results</h3>
          </div>
          <div id="area-table">
            <h4 style={{ fontSize: '18px' }}>Floor Summary</h4>
            <Table bordered columns={floor_cols} dataSource={datasourceFloor} />
          </div>
          <div id="area-table">
            <h4 style={{ fontSize: '18px' }}>Zone-Area Constraints</h4>
            <Table bordered columns={area_cols} dataSource={datasourceArea} />
          </div>
          <div id="gen-table">
            <h4 style={{ fontSize: '18px' }}>General Constraints</h4>
            <Table bordered columns={columns} dataSource={datasourceGen} />
          </div>
          <div id="zone-table">
            <h4 style={{ fontSize: '18px' }}>Zone-Specific Constraints</h4>
            <Table bordered columns={columns} dataSource={datasourceZone} />
          </div>
        </div>
      </div>
    );
  }
}

export default EvaluationView;
