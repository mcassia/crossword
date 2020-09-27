import React from 'react';
import logo from './logo.svg';
import './App.css';
import {getCluesAndBoard, Clue, Direction} from './api'


const BASE_TEMPLATE = [
  [0,0,0,0,0,0,0,0,0],
  [0,1,1,1,1,1,1,1,0],
  [0,0,0,1,0,0,0,0,0],
  [0,1,1,1,1,1,1,1,0],
  [0,0,0,1,0,0,0,1,0],
  [0,1,1,1,1,1,1,1,0],
  [0,1,0,1,0,0,1,0,0],
  [0,1,0,0,0,1,1,1,0],
  [0,0,0,0,0,0,0,0,0],
]

const CELL_SIZE = 45

function Grid(
  props: {
    board: string[][],
    template: (number|boolean)[][],
    editingMode: boolean,
    setValue: (row: number, column: number, value?: string) => void,
    toggleTemplate: (row: number, column: number) => void,
    onCellSelected: (row: number, column: number) => void,
    clues?: Clue[],
  }
) {

  // const [board, setBoard] = React.useState(props.board)
  // const [template, setTemplate] = React.useState(props.template)
  const board = props.board
  const template = props.template

  function getCell(row: number, column: number) {

    let index: number = 0
    props.clues && props.clues.forEach(
      (clue) => {
        if (clue.row === row && clue.column === column) {
          index = clue.index
        }
      }
    )

    if (!template[row][column]) {
      return (
        <div
          onClick={e=>{props.editingMode && props.toggleTemplate(row, column)}}
          style={{cursor: props.editingMode ? 'pointer' : 'default', width: CELL_SIZE, height: CELL_SIZE, backgroundColor: 'black' }}
        >
        </div>
      )
    } else {
      return (
        <div
          onClick={e=>{props.editingMode && props.toggleTemplate(row, column)}}
          style={{cursor: props.editingMode ? 'pointer' : 'default', width: CELL_SIZE, height: CELL_SIZE, backgroundColor: 'white' }}
        >
          <div style={{textAlign: 'center', position:'absolute', marginLeft:3, fontSize: 12, height: 12}}>{index > 0 ? index.toString() : ''}</div>
          {
            ( 
              !props.editingMode &&
                <input
                  onFocus={e=>{props.onCellSelected(row, column)}}
                  value={props.board[row][column]}
                  type={'text'}
                  style={{width: CELL_SIZE-8, height: CELL_SIZE-6, textAlign:'center'}}
                  onChange={e => {props.setValue(row, column, e.target.value)}}
                  disabled={props.clues && props.clues.length > 0 ? false : true}
                />
            )
          }
        </div>
      )
    }
  }

  function getMatrix() {
    return (<div>
        {
          template.map(
            (row, i) => {
              return (
                <div style={{display: 'flex'}}>
                  {
                    row.map(
                      (column, j) => {
                        return getCell(i, j)
                      }
                    )
                  }
                </div>
              )
            }
          )
        }
    </div>)
  }

  return (<div>{getMatrix()}</div>)

}

function getInitialBoardFromTemplate(template: (boolean|number)[][]) {

  const board: string[][] = []

  template.forEach(
    (row, i) => {
      const r: string[] = []
      row.forEach(
        (value, j) => {
          r.push('')
        }
      )
      board.push(r)
    }
  )

  return board
}

function getExpectedBoard(template: (boolean|number)[][], clues: Clue[]) {
  const board: string[][] = []
  template.forEach(
    (r)=>{
      const row: string[] = []
      r.forEach(()=>{row.push('')})
      board.push(row)
    }
  ) 

}

function Game() {

  const [retrievedClues, setRetrievedClues] = React.useState<boolean>();
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [template, setTemplate] = React.useState<(boolean|number)[][]>(BASE_TEMPLATE);
  const [board, setBoard] = React.useState<string[][]>(getInitialBoardFromTemplate(template));
  const [expectedBoard, setExpectedBoard] = React.useState<string[][]>([]);
  const [clues, setClues] = React.useState<Clue[]>([]);
  const [editingMode, setEditingMode] = React.useState<boolean>(false);
  const [selectedCell, setSelectedCell] = React.useState<{row: number, column: number}>();

  React.useEffect(
    () => {

      !editingMode && getCluesAndBoard(template).then(
        (result) => {
          setRetrievedClues(result.completed)
          setIsLoading(false);
          setClues(result.clues);
          setExpectedBoard(result.board)
        }
      )
    }, [template, editingMode]
  )
  React.useEffect(() => { setBoard(getInitialBoardFromTemplate(template))}, [template])

  function updateCell(row: number, column: number, value?: string) {
    const b = getClonedBoard()
    b[row][column] = value || ''
    setBoard(b)
  }

  function getClonedBoard() {
    const b: string[][] = []
    board.forEach(
      (row) => {
        const r: string[] = []
        row.forEach(
          (v) => {
            r.push(v)
          }
        )
        b.push(r)
      }
    )
    return b
  }

  function getClonedTemplate() {
    const b: (boolean|number)[][] = []
    template.forEach(
      (row) => {
        const r: (boolean|number)[] = []
        row.forEach(
          (v) => {
            r.push(v)
          }
        )
        b.push(r)
      }
    )
    return b
  }

  function validate() {
    const b = getClonedBoard()
    board.forEach(
      (row, i) => {
        row.forEach(
          (v, j) => {
            if (v !== expectedBoard[i][j]) {
              
            }
            b[i][j] = v !== expectedBoard[i][j] ? '' : v
          }
        )
      }
    )
    setBoard(b)
  }

  function toggleTemplate(row: number, column: number) {
    const t = getClonedTemplate()
    t[row][column] = t[row][column] ? 0 : 1
    setTemplate(t)
    setClues([])
    setExpectedBoard([])
  }

  function toggleEditingMode() {
    if (editingMode) {
      setIsLoading(true)
      setEditingMode(false)
    } else {
      setClues([])
      setExpectedBoard([])
      setEditingMode(true)
    }
  }

  function reveal() {
    if (!selectedCell) {
      return
    }
    const b = getClonedBoard()
    b[selectedCell.row][selectedCell.column] = expectedBoard[selectedCell.row][selectedCell.column]
    setBoard(b)
    console.log(selectedCell)
  }

  function getCluesView() {

    if (isLoading) {
      return <div>Loading...</div>
    } else if (!retrievedClues) {
      return <div>Failed to build.</div>
    }

    return clues.map(
      (clue) => {
        const text = `${clue.index}${clue.direction.toString().substr(0, 1)} ${clue.definitions[0]}`
        const isSelected = selectedCell && selectedCell.row === clue.row && selectedCell.column === clue.column
        const x = (
          <div style={{display:'flex', width: '90%', marginLeft: '5%', marginBottom: 16}}>
            <div style={{width: '10%'}}>{clue.index}</div>
            <div style={{width: '10%'}}>{clue.direction.toString().substr(0, 1)}</div>
            <div style={{width: '80%'}}>{clue.definitions[0]}</div>
          </div>
        )
        return isSelected ? <b>{x}</b> : x
      }
    )
  }

  const [height, width] = [template.length, template[0].length]

  return (
    <div style={{position:'absolute',width: '100%', height: '100%', margin: 0, padding: 0, display: 'flex'}}>
      <div style={{width: '50%', height: '100%', margin: 0, padding: 0, backgroundColor: 'rgb(220,220,220)'}}>
        <div style={{marginTop: 48, marginLeft: `calc(50% - ${(width*CELL_SIZE)/2}px)`}}>
          <Grid clues={clues} onCellSelected={(row:number,column:number)=>{setSelectedCell({row:row,column:column})}} template={template} board={board} setValue={updateCell} toggleTemplate={toggleTemplate} editingMode={editingMode}/>
        </div>
        <div style ={{textAlign: 'center', justifyContent: 'space-around', marginTop: 48,display: 'block', width: '100%', height: 48, bottom: 0, left: 0}}>
          <div style={{marginBottom: 8}}><button disabled={isLoading || editingMode || !clues || clues.length === 0} onClick={e=>{validate() }}>Validate</button></div>
          <div style={{marginBottom: 8}}><button disabled={selectedCell ? false : true} onClick={e=>{reveal() }}>Reveal Cell</button></div>
          <div style={{marginBottom: 8}}><button disabled={isLoading} onClick={e=>{toggleEditingMode()}}>{editingMode ? 'Turn Off Editing Mode' : 'Turn On Editing Mode'}</button></div>
        </div>
      </div>
      <div style={{width: '50%', margin: 0, padding: 0, paddingTop: 64}}>
        {
          getCluesView()
        }
      </div>
    </div>
  )

}

function App() {

  

  return <Game />
}

export default App;
