import random
import zipfile
import os
from math import floor
 


class MultiFile(object):
  def __init__(self, file_name, max_file_size,verbose=False):
    self.current_position = 0
    self.file_name = file_name
    self.max_file_size = max_file_size
    self.current_file = None  
    self.verbose = verbose     
    self.open_next_file()
    

 

  @property
  def current_file_no(self):
    return self.current_position / self.max_file_size



  @property
  def current_file_size(self):
    return self.current_position % self.max_file_size



  @property
  def current_file_capacity(self):
    return self.max_file_size - self.current_file_size



  def open_next_file(self):
      file_name = "%s.zip.%03d" % (self.file_name[:-4],
        self.current_file_no + 1)
      if self.verbose: print("* Opening file '%s'..." % file_name)
      if self.current_file is not None:
          self.current_file.close()
      self.current_file = open(file_name, 'wb')



  def tell(self):
      if self.verbose: print("MultiFile::Tell -> %d" % self.current_position)
      return self.current_position



  def write(self, data):
      start, end = 0, len(data)
      if self.verbose: print("MultiFile::Write (%d bytes)" % len(data))
      while start < end:
          current_block_size = min(end - start, self.current_file_capacity)
          self.current_file.write(data[start:start+current_block_size])
          if self.verbose: print("* Wrote %d bytes." % current_block_size)
          start += current_block_size
          self.current_position += current_block_size
          if self.current_file_capacity == self.max_file_size:
              self.open_next_file()
          if self.verbose: print("* Capacity = %d" % self.current_file_capacity)


  def flush(self):
      if self.verbose: print("MultiFile::Flush")
      self.current_file.flush()


class MultiFileRead(object):
  def __init__(self,src_dir,file_name,verbose=False):
    self.current_position = 0
    self.current_position_file = 0
    self.src_dir = src_dir
    self.file_name = src_dir + file_name
    #self.max_file_size = max_file_size
    self.total_zip_size = 0
    self.current_file = None  
    self.verbose = verbose  
    self.get_total_zip_size()

  @property
  def current_file_no(self):
    return floor(self.current_position / self.max_file_size) + 1
  @property
  def current_file_size(self):
    return self.current_position % self.max_file_size
  @property
  def current_file_capacity(self):
    return self.max_file_size - self.current_file_size

  def get_total_zip_size(self):
    self.max_file_size = 0
    for root, dirs, files in os.walk(self.src_dir):
      for file in files:
        file_name = os.path.join(root,file)
        with open(file_name, 'rb') as f:
          f.seek(0,2)
          #print('{0:d},{1:d}'.format(f.tell(),self.max_file_size))
          file_size = f.tell()
          self.total_zip_size += file_size
          self.max_file_size = max(self.max_file_size,file_size)
         
    if self.verbose:
      print('Total zip file size {0:d} bytes'.format(self.total_zip_size))
      print('Max zip file size {0:d} bytes'.format(self.max_file_size))

  def open_next_file(self):
    file_name = "%s.zip.%03d" % (self.file_name[:-4],self.current_file_no)
    if self.verbose: print("* Opening file '%s'..." % file_name)
    if self.current_file is not None:
        self.current_file.close()
    self.current_file = open(file_name, 'rb')
  
  def seek(self,startdir,offset=0):
    if offset == 0:
      self.current_position = startdir 
    else:
      self.current_position = self.total_zip_size + startdir
    if self.verbose: print("MultiFile::Seek -> ",startdir,offset,self.current_position)
    self.open_next_file()
    self.current_position_file = self.current_position % self.max_file_size  
    self.current_file.seek(self.current_position_file,0)
    #print("!!!!!!!!!!!   ",self.current_file.tell(),"  ",tmpstartdir)
  
  def tell(self):
    if self.verbose: print("MultiFile::Tell -> %d" % self.current_position)
    return self.current_position

  def read(self,block_size=None):
    if self.verbose:
       if block_size: 
         print("MultiFile::Read {0:d} bytes".format(block_size))
    data = b'' 
    file_capacity = self.current_file_capacity
    if self.verbose: print("Read Current File capacity "
      "{0:d} bytes".format(file_capacity))
    if block_size and block_size > file_capacity:
      block_size1 = file_capacity
      block_size2 = block_size - block_size1  
      data += self.current_file.read(block_size1)
      self.current_position += block_size1
      self.open_next_file()
      data += self.current_file.read(block_size2)
      self.current_position += block_size2
    else: 
      data += self.current_file.read(block_size)
      if block_size:
        self.current_position += block_size

    return data

    
 

def zipfiles():
  srcdir = 'test4/'
  trgdir = 'test5/'
  zipn = 'test.zip'
  size = 0.0001 # in GB

 

  mfo = MultiFile(trgdir+zipn,int(size*1024*1024*1024))
  zf = zipfile.ZipFile(mfo,mode='w',compression=zipfile.ZIP_DEFLATED)


  for root, dirs, files in os.walk(srcdir):
    for file in files:
      filename = os.path.join(root, file)
      print("Adding file '%s'..." % filename)
      zf.write(filename)

     

def unzipfiles():
  srcdir = 'test5/'
  zipn = 'test.zip'
  size = 0.0001
  mfo = MultiFileRead(srcdir,zipn,verbose=True)
  zf = zipfile.ZipFile(mfo,mode='r',compression=zipfile.ZIP_DEFLATED)
  #for root, dirs, files in os.walk(srcdir):
  #  for file in files:
  #    filename = os.path.join(root, file)
  #    print("Extracting file '%s'..." % filename)
      #print( zipfile.is_zipfile(filename))
  zf.extractall()
  #print(zf.namelist())



  return 0

 

if __name__ == '__main__':
  #zipfiles()
  unzipfiles() 

























